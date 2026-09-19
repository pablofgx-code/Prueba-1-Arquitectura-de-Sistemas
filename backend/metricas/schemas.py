from pydantic import BaseModel

class DashboardMetrics(BaseModel):
    total_personas_registradas: int
    total_alimentos_mes_actual: int