from typing import List, Dict
import logging
from services.scraper_service import scrape_category
from services.gsheet_service  import upload_rows_to_gsheet
from services.webhook_service import notify_webhook   
from starlette.concurrency import run_in_threadpool
from services.slug_service import get_slug

logger = logging.getLogger(__name__)

async def run_scraping_flow(category: str, webhook: str, email: str) -> None:
    try:
        slug = await get_slug(category)
        rows: List[Dict[str, str]] = await run_in_threadpool(scrape_category, category, slug)
        sheet_links = await run_in_threadpool(upload_rows_to_gsheet, rows, category)

        if sheet_links is None:
                logger.error(" Falló la subida a GSheet, no se notificará webhook.")
                return
        
        sheet_url = sheet_links["url_to_tab"]
        success = await notify_webhook(webhook, email, sheet_url)
        if not success:
            logger.warning(f" Falló notificación al webhook: {webhook}")

    except Exception as e:
        logger.exception(f"Error inesperado en run_scraping_flow: {e}")
    

