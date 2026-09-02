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

class CambiarPassword(BaseModel):
    
    password_actual: str    
    nueva_password: str = Field(..., min_length=6, description="Debe tener al menos 6 caracteres")

class SolicitudRecuperacion(BaseModel):
    
    email: str

class RestablecerPassword(BaseModel):
    
    token: str = Field(..., description="Token JWT de Recuperacion")
    nueva_password: str = Field(..., min_length=6, description="Al menos debe tener 6 caracteres")

