from datetime import datetime, timedelta
import requests, bs4, re, unicodedata
from typing import Optional
from datetime import datetime, timezone


CACHE_TTL = timedelta(hours=10)

_cached_slug_map = None
_cached_slug_map_timestamp = None

def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text.lower()).strip()

def _rebuild_slug_map() -> dict:
    html = requests.get("https://xepelin.com/blog", timeout=10).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    return {
        _normalize(a.text): a["href"].split("/blog/")[1].strip("/")
        for a in soup.select("nav ul li a[href^='https://xepelin.com/blog/']")
        if a.text.strip()
    }

def get_slug(category_name: str) -> Optional[str]:
    global _cached_slug_map, _cached_slug_map_timestamp
    now = datetime.now(timezone.utc)
    if (
        _cached_slug_map is None or
        _cached_slug_map_timestamp is None or
        now - _cached_slug_map_timestamp > CACHE_TTL
    ):
        _cached_slug_map = _rebuild_slug_map()
        _cached_slug_map_timestamp = now
    return _cached_slug_map.get(_normalize(category_name))

def get_all_slugs() -> dict:
    global _cached_slug_map, _cached_slug_map_timestamp
    now = datetime.now(timezone.utc)
    if (
        _cached_slug_map is None or
        _cached_slug_map_timestamp is None or
        now - _cached_slug_map_timestamp > CACHE_TTL
    ):
        _cached_slug_map = _rebuild_slug_map()
        _cached_slug_map_timestamp = now
    return _cached_slug_map.copy()
