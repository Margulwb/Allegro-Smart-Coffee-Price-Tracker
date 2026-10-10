import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.tools import get_price_history

client = TestClient(app)


def test_health_ready_and_demo_offer() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready"}
    assert client.get("/api/v1/offers").json()[0]["price_pln"] == 54.90


def test_metrics_include_demo_offer() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert 'allegro_coffee_price_pln{product="jacobs_kronung_1kg"' in response.text


def test_alert_uses_deterministic_fallback(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "")
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    response = client.post(
        "/api/v1/alerts",
        json={
            "alerts": [
                {
                    "status": "firing",
                    "labels": {"product": "jacobs_kronung_1kg"},
                    "annotations": {"description": "Current price: 49.90 PLN."},
                }
            ]
        },
    )
    assert response.status_code == 200
    assert response.json()["processed"] == 1
    assert response.json()["summaries"][0]["advisor"] == "fallback"
    assert response.json()["summaries"][0]["delivery"] == "log"


def test_agent_tool_rejects_invalid_product_selector() -> None:
    result = asyncio.run(get_price_history('coffee"} or on()'))
    assert result == {"error": "Invalid product identifier."}
