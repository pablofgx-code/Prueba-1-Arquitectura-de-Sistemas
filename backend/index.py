
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "active_page": "home"}
    )

@router.get("/donaciones-semanales", response_class=HTMLResponse, name="donaciones_semanales")
async def donaciones_semanales(request: Request):
    return templates.TemplateResponse(
        "pages/donaciones_semanales.html",
        {"request": request, "active_page": "donaciones_semanales"}
    )

@router.get("/personas", response_class=HTMLResponse, name="personas")
async def personas(request: Request):
    return templates.TemplateResponse(
        "pages/personas.html",
        {"request": request, "active_page": "personas"}
    )

@router.get("/donaciones-mensuales", response_class=HTMLResponse, name="donaciones_mensuales")
async def donaciones_mensuales(request: Request):
    return templates.TemplateResponse(
        "pages/donaciones_mensuales.html",
        {"request": request, "active_page": "donaciones_mensuales"}
    )
