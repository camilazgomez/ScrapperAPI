from typing import List, Dict
from services.scraper_service import scrape_category
from services.gsheet_service  import upload_rows_to_gsheet
from services.webhook_service import notify_webhook   
import os

REQUEST_EMAIL = os.getenv("REQUEST_EMAIL")

def run_scraping_flow(category: str, webhook: str) -> None:
    rows: List[Dict[str, str]] = scrape_category(category)
    sheet_links = upload_rows_to_gsheet(rows, category)
    sheet_url = sheet_links["url_to_tab"]
    notify_webhook(webhook, REQUEST_EMAIL, sheet_url)
    

