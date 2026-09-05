from datetime import date
from beanie import Document
from typing import Optional, List

class Perfil(Document):
    nombre: str
    apellido: str
    rut: str
    contacto: Optional[str] = None  
    fecha_nacimiento: date
    edad: int
    situacion_calle: bool = False
    motivo_situacion: Optional[str] = None 
    historial_retiros: List[date] = []

    class Settings:
        name = "perfiles"