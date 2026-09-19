from beanie import Document
from datetime import date
from pydantic import Field

class LotePerecible(Document):

    tipo_alimento: str = Field(..., description = "Ej: Arroz, Leche")
    cantidad_disponible: int = Field(..., ge = 0)
    fecha_vencimiento: date = Field(..., description = "Fecha en la que caduca este lote")

    class Settings:

        name = "bodega_central"

