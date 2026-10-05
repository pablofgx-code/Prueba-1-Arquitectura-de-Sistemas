from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from backend.database import iniciar_base_de_datos
from backend.database_seed import poblar_base_de_datos
from backend.perfiles.router import router as perfiles_router
from backend.auth.router import router as auth_router
from backend.auth.dependencies import obtener_admin_actual
from backend.donaciones.router import router as donaciones_router
from backend.inventario.router import router as inventario_router
from backend.metricas.router import router as metricas_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await iniciar_base_de_datos()
    await poblar_base_de_datos()
    yield


app = FastAPI(
    title="Sistema de Donaciones Iglesia",
    lifespan=lifespan
)

# Routers de la API REST (JSON)
app.include_router(perfiles_router)
app.include_router(auth_router)
app.include_router(donaciones_router)
app.include_router(inventario_router)
app.include_router(metricas_router)

# Configuración de Templates Jinja2 y Archivos Estáticos
templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/services", StaticFiles(directory="frontend/services"), name="services")


# Si una PÁGINA da 401 (sin sesión o token vencido) -> redirige al login.
# Si es la API (/api/...), mantiene el JSON de error normal.
@app.exception_handler(StarletteHTTPException)
async def manejar_http_exception(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 401 and not request.url.path.startswith("/api"):
        return RedirectResponse(url=request.url_for("login_page"), status_code=303)
    return await http_exception_handler(request, exc)


# Dependencia para las páginas privadas
privada = [Depends(obtener_admin_actual)]


# Rutas para renderizar las páginas HTML
@app.get("/", response_class=HTMLResponse, name="home", dependencies=privada)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/home.html",
        context={"request": request, "active_page": "home"}
    )

@app.get("/login", response_class=HTMLResponse, name="login_page")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "active_page": "login"}
    )

@app.get("/cambiar-contrasena", response_class=HTMLResponse, name="cambiar_contrasena", dependencies=privada)
def cambiar_contrasena_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/login/cambiar_contrasena.html",
        context={"request": request, "active_page": "cambiar_contrasena"}
    )

@app.get("/donaciones-semanales", response_class=HTMLResponse, name="donaciones_semanales", dependencies=privada)
def donaciones_semanales(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/donacionesSemanales.html",
        context={"request": request, "active_page": "donaciones_semanales"}
    )

@app.get("/personas", response_class=HTMLResponse, name="personas", dependencies=privada)
def personas(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/perfilPersonas.html",
        context={"request": request, "active_page": "personas"}
    )

@app.get("/donaciones-mensuales", response_class=HTMLResponse, name="donaciones_mensuales", dependencies=privada)
def donaciones_mensuales(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/retirosMensuales.html",
        context={"request": request, "active_page": "donaciones_mensuales"}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)