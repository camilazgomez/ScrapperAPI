import logging
from typing import Dict, List
from bs4 import BeautifulSoup
import os
import gc
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from utils.html_utils import ( click_all_load_more, extract_read_time, split_author,)

BASE_URL = "https://xepelin.com/blog/"
logger   = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _get_driver() -> webdriver.Chrome:
    opts = uc.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.binary_location = os.getenv("CHROME_BIN", "/usr/bin/chromium")

    version_main = int(os.getenv("CHROME_VERSION_MAIN"))

    uc_driver_path = os.path.expanduser(
        "~/.local/share/undetected_chromedriver/undetected_chromedriver"
    )

    return uc.Chrome(
        options=opts,
        version_main=version_main,
        driver_executable_path=uc_driver_path,
    )

# Realiza scraping sobre una categoría específica del blog.
# Devuelve una lista de artículos con título, autor, rol, categoría y tiempo de lectura.
def scrape_category(category: str, slug: str) -> List[Dict[str, str]]:
    if not slug:
        logger.warning("Categoría '%s' no encontrada en el blog", category)
        return []

    url   = BASE_URL + slug
    rows: List[Dict[str, str]] = []

    driver = _get_driver()
    try:
        logger.info("Abriendo %s", url)
        driver.get(url)

        wait = WebDriverWait(driver, 50)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*=BlogArticle_box]")
            )
        )
        # Carga todos los artículos visibles haciendo clic en "Cargar más"
        click_all_load_more(driver)
        page_source = driver.page_source
    except TimeoutException:
        logger.warning("Timeout: no se encontraron artículos en %s", category)
        debug_path = f"debug_{category}.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info(f"Guardado HTML para debugging en {debug_path}")
        return []
    
    finally:
        driver.quit()
        gc.collect()

    try:
        soup      = BeautifulSoup(page_source, "html.parser")
        articles  = soup.select("div[class*=BlogArticle_box]")
        logger.info("Total artículos encontrados: %d", len(articles))

        for art in articles:
            title_tag = art.select_one("div[class*=BlogArticle_contentMain]")
            title     = title_tag.get_text(strip=True) if title_tag else "Sin título"
            auth_tag      = art.select_one("div[class*=BlogArticle_authorDescription]")
            author_name, author_role = split_author(auth_tag.get_text(strip=True)) if auth_tag else ("Desconocido", "Sin cargo")
            
            link_tag    = art.find("a", href=True)
            article_url = link_tag["href"]
            read_time = extract_read_time(article_url) if article_url else ""

            rows.append(
                {
                    "title":        title,
                    "category":     category,
                    "author_name":  author_name,
                    "read_time":    read_time,
                    "author_role":  author_role,
                }
            )
    except Exception as e:
        logger.exception("Error en el scraping de la categoría '%s': %s", category, str(e))
    return rows

