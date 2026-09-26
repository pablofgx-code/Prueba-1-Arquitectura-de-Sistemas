import uvicorn

from backend.database import iniciar_base_de_datos
from backend.database_seed import poblar_base_de_datos


from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager




from backend.database import iniciar_base_de_datos
from backend.perfiles.router import router as perfiles_router
from backend.auth.router import router as auth_router
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

app.include_router(perfiles_router)
app.include_router(auth_router)
app.include_router(donaciones_router)
app.include_router(inventario_router)
app.include_router(metricas_router)

# Templates Jinja2
templates = Jinja2Templates(
    directory="frontend/templates"
)


# Archivos estáticos: CSS, JS, imágenes
app.mount(
    "/static",
    StaticFiles(directory="frontend/static"),
    name="static"
)


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "index.html", 
        context = {"request": request, "mensaje": "Backend y base de datos conectada xd"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )