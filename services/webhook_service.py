from typing import Final
import logging
import httpx

logger = logging.getLogger(__name__)
TIMEOUT: Final[int] = 10  

async def notify_webhook( webhook_url: str, email: str, sheet_link: str,) -> bool:
    payload = {"email": email, "link": sheet_link}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp =  await client.post(webhook_url, json=payload)
            resp.raise_for_status()
            logger.info(
                "[webhook_service] Webhook %s notified (status=%s)",
                webhook_url,
                resp.status_code,
            )
            return True

    except Exception as exc:
        logger.error(
            "[webhook_service] Could not notify %s → %s",
            webhook_url,
            exc,
            exc_info=True,
        )
        return False