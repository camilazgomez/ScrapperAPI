from urllib.parse import urlparse
import httpx

def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def is_reachable_url(url: str, timeout: int = 5) -> bool:
    try:
        resp = httpx.head(url, timeout=timeout, follow_redirects=True)
        return resp.status_code < 400
    except Exception:
        return False
