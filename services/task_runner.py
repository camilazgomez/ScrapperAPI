from typing import List, Dict
import logging
from services.scraper_service import scrape_category
from services.gsheet_service  import upload_rows_to_gsheet
from services.webhook_service import notify_webhook   
import os
logger = logging.getLogger(__name__)

def run_scraping_flow(category: str, webhook: str, email: str) -> None:
    rows: List[Dict[str, str]] = scrape_category(category)
    sheet_links = upload_rows_to_gsheet(rows, category)
    sheet_url = sheet_links["url_to_tab"]
    success = notify_webhook(webhook, email, sheet_url)
    if not success:
        logger.warning(f"[task_runner] Falló notificación al webhook: {webhook}")
    

