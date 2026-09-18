from pydantic import BaseModel, Field

class InicializarMes(BaseModel):
    year: int = Field(..., ge=2024)
    mes: int = Field(..., ge=1, le=12)

class AgregarDonaciones(BaseModel): 
    numero_semana: int = Field(..., ge=1, le=5)
    tipo_alimento: str = Field(..., min_length=2)
    cantidad: int = Field(..., ge=1)

class ResumenTotalMes(BaseModel):
    year: int
    mes: int
    total_alimentos_donados: int

class ModificarFecha(BaseModel):
    nueva_fecha: str = Field(
        ...,
        description="Formato estricto: DD/MM/YYYY",
        pattern=r"^\d{2}/\d{2}/\d{4}$"
    )





