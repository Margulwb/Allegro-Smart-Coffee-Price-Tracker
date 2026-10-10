import os

import httpx


async def send_discord_notification(message: str) -> bool:
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return False
    async with httpx.AsyncClient(timeout=8.0) as client:
        response = await client.post(webhook_url, json={"content": message[:1900]})
        response.raise_for_status()
    return True
