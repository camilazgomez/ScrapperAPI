import re
import unicodedata
from typing import Tuple, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text.lower()).strip()


def split_author(text: str) -> Tuple[str, str]:
    parts = [p.strip() for p in text.split("|", 1)]
    name  = parts[0] if parts else "Desconocido"
    role  = parts[1] if len(parts) > 1 else "Sin cargo"
    return name, role


def click_all_load_more(driver: WebDriver, timeout: int = 8) -> None:
    while True:
        try:
            btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(translate(., "
                        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ', "
                        "'abcdefghijklmnopqrstuvwxyzáéíóú'), "
                        "'cargar más')]",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", btn)
        except Exception:
            break


def extract_read_time(driver: WebDriver, url: str, timeout: int = 8) -> str:
    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.Text_body__snVk8"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        txt_div = soup.select_one("div.Text_body__snVk8")
        if not txt_div:
            return ""
        m = re.search(r"(\d+)\s*min", txt_div.get_text(strip=True).lower())
        return f"{m.group(1)}min" if m else ""
    except Exception:
        return ""
