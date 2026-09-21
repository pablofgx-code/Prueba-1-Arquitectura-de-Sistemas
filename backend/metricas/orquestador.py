from datetime import datetime
from backend.metricas.schemas import DashboardMetrics
from backend.perfiles.service import PerfilService
from backend.donaciones.service import DonacionService
from backend.inventario.service import InventarioService

class ObtenerMetricasOrquestador:

    def __init__(
        self, perfil_service: PerfilService, 
        donacion_service: DonacionService,
        inventario_service: InventarioService
    ):
        self.perfil_service = perfil_service
        self.donacion_service = donacion_service
        self.inventario_service = inventario_service

    async def ejecutar(self) -> DashboardMetrics:
        hoy = datetime.now()

        total_personas = await self.perfil_service.contar_total_perfiles()

        ingresados = await self.donacion_service.contar_alimentos_mes_actual(hoy.year, hoy.month)

        salidos = await self.inventario_service.contar_salidas_mes_actual(hoy.year, hoy.month)

        bodega = await self.inventario_service.obtener_resumen_agrupado()

        return DashboardMetrics(
            total_personas_registradas = total_personas,
            total_alimentos_ingresados_mes = ingresados,
            total_alimentos_salidos_mes = salidos,
            inventario_actual = bodega
        )
    