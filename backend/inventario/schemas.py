from pydantic import BaseModel
from beanie import PydanticObjectId

class ItemInventarioResponse(BaseModel):
    id: PydanticObjectId
    tipo_alimento: str
    cantidad_disponible: int


