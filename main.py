from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv
from services.slug_service import get_all_slugs, get_slug
from services.task_runner import run_scraping_flow
from utils.validation_url_utils import is_valid_url, is_reachable_url


load_dotenv()
DEFAULT_EMAIL = os.getenv("REQUEST_EMAIL")

app = FastAPI()

class ScrappingInformation(BaseModel):
    category: str
    webhook: str
    email: EmailStr | None = None

@app.post("/blog-scraper", description="Puedes enviar una categoría del blog para su escrapeo, y All para escrapear todas.")
async def trigger_scraper(data: ScrappingInformation, tasks: BackgroundTasks):
    if data.category.lower() != ("all" or "All") :
        slug = await  get_slug(data.category)
        if not slug:
            raise HTTPException(status_code=400,
                                detail=f"Categoría '{data.category}' no existe en el blog")
    
    if not is_valid_url(data.webhook):
        raise HTTPException(status_code=400,
                            detail=f"URL de webhook inválida: {data.webhook}")

    if not await is_reachable_url(data.webhook):
        raise HTTPException(status_code=400,
                            detail=f"No se pudo contactar la URL del webhook: {data.webhook}")
    
    email = data.email or DEFAULT_EMAIL    
    tasks.add_task(run_scraping_flow, data.category, data.webhook, email)
    return {
        "status":   "accepted",
        "detail":   f"Se inició el scraping para '{data.category}'. Se notificara al webhook al finalizar.",
        "email_answers_to": email
    }


@app.get("/slugs")
async def list_available_slugs():
    """Devuelve el mapa de slugs cacheado."""
    return await get_all_slugs()
