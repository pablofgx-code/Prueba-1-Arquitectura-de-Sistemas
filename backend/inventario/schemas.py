from pydantic import BaseModel
from beanie import PydanticObjectId
from datetime import date

class LotePerecibleResponse(BaseModel):
    id: PydanticObjectId
    tipo_alimento: str
    cantidad_disponible: int
    fecha_vencimiento: date

