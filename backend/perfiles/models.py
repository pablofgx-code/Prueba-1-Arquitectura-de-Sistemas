from beanie import Document
from pydantic import Field
from typing import Optional

class Perfil(Document):
    nombre: str
    apellido: str
    rut: str
    contacto: Optional[str] = None  
    fecha_nacimiento: str
    edad: int
    situacion_calle: bool = False
    motivo_situacion: Optional[str] = None 

    class Settings:
        name = "perfiles"