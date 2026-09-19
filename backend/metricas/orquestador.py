from datetime import datetime
from backend.metricas.schemas import DashboardMetrics
from backend.perfiles.service import PerfilService
from backend.donaciones.service import DonacionService

class ObtenerMetricasOrquestador:

    def __init__(self, perfil_service: PerfilService, donacion_service: DonacionService):
        self.perfil_service = perfil_service
        self.donacion_service = donacion_service

    async def ejecutar(self) -> DashboardMetrics:
        hoy = datetime.now()

        total_personas = await self.perfil_service.contar_total_perfiles()

        total_alimentos = await self.donacion_service.contar_alimentos_mes_actual(hoy.year, hoy.month)

        return DashboardMetrics(
            total_personas_registradas = total_personas,
            total_alimentos_mes_actual = total_alimentos
        )
    