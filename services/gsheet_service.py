from __future__ import annotations

import os
import time
import logging
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlencode, urlsplit, urlunsplit
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import requests
from google.auth.exceptions import TransportError

load_dotenv()
logger = logging.getLogger(__name__)

CREDS_PATH: Path | None = None
_raw_path = os.getenv("GOOGLE_CREDS_PATH")
if _raw_path:
    CREDS_PATH = Path(_raw_path).expanduser().resolve()

SPREADSHEET_URL: str | None = os.getenv("GOOGLE_SPREADSHEET_URL")
SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
)

if CREDS_PATH is None or not CREDS_PATH.exists():
    raise RuntimeError("[gsheet_service] GOOGLE_CREDS_PATH no definido o no existe")

if SPREADSHEET_URL is None:
    raise RuntimeError("[gsheet_service] GOOGLE_SPREADSHEET_URL no definido")

_gclient: gspread.Client | None = None
MAX_RETRIES = 3
RETRY_BACKOFF = 5 

def _get_client() -> gspread.Client:
    global _gclient
    if _gclient is None:
        creds = Credentials.from_service_account_file(
            CREDS_PATH, scopes=SCOPES
        )
        _gclient = gspread.authorize(creds)
    return _gclient

HEADER_MAP = {
    "title":        "Title",
    "category":     "Category",
    "author_name":  "Author",
    "read_time":    "Read Time",
    "author_role":  "Author Role",
}


def upload_rows_to_gsheet(rows: List[Dict[str, str]], category: str) -> Dict[str, str]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = _get_client()
            sh = client.open_by_url(SPREADSHEET_URL)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            worksheet_title = f"{category}-{timestamp}"
            ws = sh.add_worksheet(
                title=worksheet_title,
                rows=str(len(rows) + 1),
                cols=str(len(HEADER_MAP)),
            )
            ws.append_row(list(HEADER_MAP.values()))

            ordered_rows = [
                [row.get(key, "") for key in HEADER_MAP.keys()]
                for row in rows
            ]
            if ordered_rows:
                ws.append_rows(ordered_rows, value_input_option="RAW")

            gid = ws.id  
            parsed = urlsplit(sh.url)
            url_to_tab = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode({"gid": gid}), ""))
            return {
                "url_base": sh.url.split("/edit")[0],
                "url_to_tab": url_to_tab,
            }
        
        except (gspread.exceptions.APIError, requests.exceptions.RequestException, TransportError) as e:
                logger.warning(f"[GSheet] Intento {attempt} fallido: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF * attempt)
                else:
                    logger.error("[GSheet] Todos los intentos fallaron al subir datos a Google Sheets.")
                    return None