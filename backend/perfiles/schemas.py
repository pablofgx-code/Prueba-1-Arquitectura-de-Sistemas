from pydantic import BaseModel, Field
from typing import Optional, List
from beanie import PydanticObjectId
from datetime import date

class PerfilCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre del beneficiario")
    apellido: str = Field(..., min_length=2, max_length=50)
    rut: str = Field(..., min_length=8, max_length=12, description="RUT con guion")
    contacto: Optional[str] = Field(None, max_length=20)
    fecha_nacimiento: date
    edad: int = Field(..., ge=0, le=120, description= "la edad debe ser un numero real")
    situacion_calle: bool = False
    motivo_situacion: Optional[str] = None

class PerfilResponse(PerfilCreate):
    id: PydanticObjectId
    historial_retiros: List[date] = []




