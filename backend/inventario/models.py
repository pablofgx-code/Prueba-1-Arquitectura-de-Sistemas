from beanie import Document
from datetime import datetime
from pydantic import Field

class LotePerecible(Document):

    tipo_alimento: str = Field(..., description = "Ej: Arroz, Leche")
    cantidad_disponible: int = Field(..., ge = 0)
    class Settings:

        name = "bodega_central"

class RegistroSalida(Document):
    fecha: datetime
    rut_beneficiario: str

    class Settings:
        name = "historial_salidas"
