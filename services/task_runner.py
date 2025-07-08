from typing import List, Dict
from services.scraper_service import scrape_category
from services.gsheet_service  import upload_rows_to_gsheet

def run_scraping_flow(category: str, webhook: str) -> None:
    rows: List[Dict[str, str]] = scrape_category(category)
    

