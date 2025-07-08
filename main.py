from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from services.slug_service import get_all_slugs, get_slug
from services.task_runner import run_scraping_flow

load_dotenv()
DEFAULT_EMAIL = os.getenv("REQUEST_EMAIL")

app = FastAPI()

class ScrappingInformation(BaseModel):
    category: str
    webhook: str

@app.post("/blog-scraper")
async def trigger_scraper(data: ScrappingInformation, tasks: BackgroundTasks):
    slug = get_slug(data.category)
    if not slug:
        raise HTTPException(status_code=400,
                            detail=f"Categoría '{data.category}' no existe en el blog")

    tasks.add_task(run_scraping_flow, data.category, data.webhook)
    return {
        "status":   "accepted",
        "detail":   f"Se inició el scraping para '{data.category}'. Se notificara al webhook al finalizar."
    }


@app.get("/slugs")
def list_available_slugs():
    """Devuelve el mapa de slugs cacheado."""
    return get_all_slugs()
