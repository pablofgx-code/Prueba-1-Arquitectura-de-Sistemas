from beanie import Document
from datetime import date, datetime
from pydantic import Field, BaseModel
from typing import List

class LotePerecible(Document):

    tipo_alimento: str = Field(..., description = "Ej: Arroz, Leche")
    cantidad_disponible: int = Field(..., ge = 0)
    fecha_vencimiento: date = Field(..., description = "Fecha en la que caduca este lote")

    class Settings:

        name = "bodega_central"

class ItemLlevado(BaseModel):
    tipo_alimento: str
    cantidad: int

class RegistroSalida(Document):
    fecha: datetime
    rut_beneficiario: str
    alimentos_entregados: List[ItemLlevado]

    class Settings:
        name = "historial_salidas"
