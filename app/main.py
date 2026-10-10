import logging
import os
from typing import Any

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest
from pydantic import BaseModel, Field
from starlette.responses import Response

from app.advisor import summarize_alert
from app.notifier import send_discord_notification

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

PRICE = Gauge(
    "allegro_coffee_price_pln",
    "Current synthetic demo price in PLN.",
    ("product", "seller"),
)
ALERTS = Counter("coffee_alerts_processed_total", "Processed price alerts.", ("advisor",))
DEMO_OFFER = {
    "product": "jacobs_kronung_1kg",
    "name": "Jacobs Kronung 1 kg (synthetic demo offer)",
    "price_pln": 54.90,
    "seller": "demo-seller",
    "smart_shipping": False,
    "url": "https://allegro.pl/",
}
PRICE.labels(
    product=DEMO_OFFER["product"], seller=DEMO_OFFER["seller"]
).set(DEMO_OFFER["price_pln"])


class AlertEvent(BaseModel):
    status: str = "firing"
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)


class AlertmanagerWebhook(BaseModel):
    status: str = "firing"
    alerts: list[AlertEvent] = Field(default_factory=list)


app = FastAPI(title="Coffee Deal Observer", version="0.1.0")


@app.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", include_in_schema=False)
async def readyz() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/api/v1/offers")
async def offers() -> list[dict[str, Any]]:
    return [DEMO_OFFER]


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/alerts")
async def receive_alerts(payload: AlertmanagerWebhook) -> dict[str, Any]:
    summaries = []
    for event in payload.alerts:
        if event.status != "firing":
            continue
        summary, advisor = await summarize_alert(event.model_dump())
        delivered = False
        try:
            delivered = await send_discord_notification(summary)
        except Exception:
            logger.exception("Discord notification failed")
        ALERTS.labels(advisor=advisor).inc()
        logger.info("Price alert (%s): %s", advisor, summary)
        summaries.append(
            {"summary": summary, "advisor": advisor, "delivery": "discord" if delivered else "log"}
        )
    return {"processed": len(summaries), "summaries": summaries}
