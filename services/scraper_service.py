import logging
from typing import Dict, List
from bs4 import BeautifulSoup
import os
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from services.slug_service import get_slug
from utils.html_utils import ( click_all_load_more, extract_read_time, split_author,)

BASE_URL = "https://xepelin.com/blog/"
logger   = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _get_driver() -> webdriver.Chrome:
    opts = uc.ChromeOptions()
    opts.headless = True
    opts.add_argument("--headless=new")     
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.binary_location = os.getenv("CHROME_BIN", "/usr/bin/chromium")
    return uc.Chrome(options=opts, version_main=None)

def scrape_category(category: str) -> List[Dict[str, str]]:
    slug = get_slug(category)
    if not slug:
        logger.warning("Categoría '%s' no encontrada en el blog", category)
        return []

    url   = BASE_URL + slug
    rows: List[Dict[str, str]] = []

    driver = _get_driver()
    try:
        logger.info("Abriendo %s", url)
        driver.get(url)

        wait = WebDriverWait(driver, 15)
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[class*=BlogArticle_box]")
                )
            )
        except TimeoutException:
            logger.warning("Timeout: no se encontraron artículos en %s", category)
            debug_path = f"debug_{category}.html"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info(f"Guardado HTML para debugging en {debug_path}")
            return []  

        click_all_load_more(driver)

        soup      = BeautifulSoup(driver.page_source, "html.parser")
        articles  = soup.select("div[class*=BlogArticle_box]")
        logger.info("Total artículos encontrados: %d", len(articles))

        for art in articles:
            title_tag = art.select_one("div[class*=BlogArticle_contentMain]")
            title     = title_tag.get_text(strip=True) if title_tag else "Sin título"
            auth_tag      = art.select_one("div[class*=BlogArticle_authorDescription]")
            author_name, author_role = split_author(auth_tag.get_text(strip=True)) if auth_tag else ("Desconocido", "Sin cargo")
            
            link_tag    = art.find("a", href=True)
            article_url = link_tag["href"]
            read_time = extract_read_time(driver, article_url) if article_url else ""

            rows.append(
                {
                    "title":        title,
                    "category":     category,
                    "author_name":  author_name,
                    "read_time":    read_time,
                    "author_role":  author_role,
                }
            )
    finally:
        driver.quit()
    return rows

