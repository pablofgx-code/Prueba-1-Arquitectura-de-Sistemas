from pydantic import BaseModel, Field
from beanie import PydanticObjectId

class AdministradorCreate(BaseModel):

    email: str = Field(..., description="Correo del Administrador")
    password: str = Field(..., min_length=6, description="Contraseña en texto plano")
    nombre: str = Field(..., min_length=2)

class AdministradorResponse(BaseModel):

    id: PydanticObjectId
    email: str
    nombre: str
    activo: bool

class LoginData(BaseModel):

    email: str
    password: str


