import asyncio
import math
import os
import re
from typing import Any

import httpx

PRODUCT_ID = re.compile(r"[a-zA-Z0-9_-]{1,80}\\Z")
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_price_history",
            "description": "Read latest offer price and its 30-day average from VictoriaMetrics.",
            "parameters": {
                "type": "object",
                "properties": {"product": {"type": "string"}},
                "required": ["product"],
            },
        },
    }
]


def _first_price(response: dict[str, Any]) -> float | None:
    results = response.get("data", {}).get("result", [])
    if not results:
        return None
    try:
        value = float(results[0]["value"][1])
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


async def get_price_history(product: str) -> dict[str, Any]:
    if not PRODUCT_ID.fullmatch(product):
        return {"error": "Invalid product identifier."}

    base_url = os.getenv("VICTORIA_METRICS_URL", "http://victoria-metrics:8428").rstrip("/")
    selector = f'allegro_coffee_price_pln{{product="{product}"}}'

    async def query(client: httpx.AsyncClient, expression: str) -> float | None:
        response = await client.get(f"{base_url}/api/v1/query", params={"query": expression})
        response.raise_for_status()
        return _first_price(response.json())

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            current, average = await asyncio.gather(
                query(client, selector), query(client, f"avg_over_time({selector}[30d])")
            )
    except (httpx.HTTPError, ValueError):
        return {"error": "VictoriaMetrics is unavailable."}

    return {"product": product, "current_price_pln": current, "average_30d_pln": average}
