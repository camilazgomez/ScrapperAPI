import logging
import asyncio
import os
from typing import List, Dict
from services.scraper_service import scrape_category
from services.gsheet_service  import upload_rows_to_gsheet
from services.webhook_service import notify_webhook   
from starlette.concurrency import run_in_threadpool
from services.slug_service import get_slug, get_all_slugs
from functools import partial
from asyncio import Semaphore



logger = logging.getLogger(__name__)
CONCURRENCY_LIMIT = int(os.getenv("CONCURRENCY_LIMIT"))

async def scrape_with_limit(cat: str, slug: str, semaphore: Semaphore):
    async with semaphore:
        return await run_in_threadpool(scrape_category, cat, slug)

async def run_scraping_flow(category: str, webhook: str, email: str) -> None:
    try:
        if category.lower() == "all":
            slugs_dict = await get_all_slugs()
            semaphore = Semaphore(CONCURRENCY_LIMIT)
            tasks = [
                    scrape_with_limit(cat, slug, semaphore)
                    for cat, slug in slugs_dict.items()
                ]
            
            all_categories_results = await asyncio.gather(*tasks, return_exceptions=True)
            all_rows = []
            for result in all_categories_results:
                if isinstance(result, Exception):
                    logger.warning("Una categoría falló: %s", result)
                else:
                    all_rows.extend(result)
            rows = all_rows
        else: 
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
    

