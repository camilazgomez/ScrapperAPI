import re
import httpx
import unicodedata
from typing import Tuple, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text.lower()).strip()

 # Separa el nombre del autor y su cargo a partir de una cadena con formato "Nombre | Cargo".
def split_author(text: str) -> Tuple[str, str]:
    parts = [p.strip() for p in text.split("|", 1)]
    name  = parts[0] if parts else "Desconocido"
    role  = parts[1] if len(parts) > 1 else "Sin cargo"
    return name, role

# Hace clic sucesivamente en el botón "Cargar más" hasta que ya no esté disponible.
def click_all_load_more(driver, wait: WebDriverWait | None = None) -> None:
    wait = wait or WebDriverWait(driver, 10)
    while True:
        try:
            btn = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(translate(., "
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ', "
                    "'abcdefghijklmnopqrstuvwxyzáéíóú'), 'cargar más')]"
                ))
            )
            driver.execute_script("arguments[0].click();", btn)
            wait.until(EC.staleness_of(btn))
        except TimeoutException:
            break 

# Extrae el tiempo estimado de lectura (en minutos) desde la URL del artículo.
def extract_read_time(article_url: str, timeout: int = 5) -> str:
    try:
        resp = httpx.get(article_url, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        txt_div = soup.select_one("div.Text_body__snVk8")
        if not txt_div:
            return ""
        m = re.search(r"(\d+)\s*min", txt_div.get_text(strip=True).lower())
        return f"{m.group(1)}min" if m else ""
    except Exception:
        return ""
