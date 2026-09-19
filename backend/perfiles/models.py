from datetime import date
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List

class ItemLlevado(BaseModel):
    tipo_alimento: str
    cantidad: int

class RegistroRetiro(BaseModel):
    fecha: date
    alimentos_llevados: List[ItemLlevado]

class Perfil(Document):
    nombre: str
    apellido: str
    rut: str
    contacto: Optional[str] = None  
    fecha_nacimiento: date
    edad: int
    situacion_calle: bool = False
    motivo_situacion: Optional[str] = None 
    historial_retiros: List[RegistroRetiro] = []

    class Settings:
        name = "perfiles"