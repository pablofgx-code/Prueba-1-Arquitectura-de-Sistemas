from pydantic import BaseModel
from typing import List

class ResumenBodega(BaseModel):
    nombre: str
    cantidad_total: int

class DashboardMetrics(BaseModel):
    total_personas_registradas: int
    total_alimentos_ingresados_mes: int
    total_alimentos_salidos_mes: int
    inventario_actual: List[ResumenBodega]