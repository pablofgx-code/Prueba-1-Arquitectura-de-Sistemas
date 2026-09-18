import uuid
from beanie import Document
from pydantic import BaseModel, Field
from typing import List

class DonacionAlimento(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tipo_alimento: str = Field(..., description="Ej: Arroz, Fideos, Leche")
    cantidad: int = Field(..., ge=1, description="Cantidad en unidades o kilos")

class Semana(BaseModel):
    numero_semana: int = Field(..., ge=1, le=5)
    donaciones: List[DonacionAlimento] = []

class MesDonacion(Document):
    year: int
    mes: int = Field(..., ge=1, le=12)
    fecha_creacion: str
    semanas: List[Semana] = []

    class Settings:
        name = "donaciones_mensuales"



