from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn

from backend.database import iniciar_base_de_datos

@asynccontextmanager
async def lifespan(app: FastAPI):
    await iniciar_base_de_datos()
    yield

app = FastAPI(title="Sistema de Donaciones Iglesia", lifespan=lifespan)

templates = Jinja2Templates(directory="frontend/templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "mensaje": "¡Backend y BD conectados!"}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)