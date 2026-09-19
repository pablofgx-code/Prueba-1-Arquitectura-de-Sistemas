from backend.donaciones.schemas import AgregarDonaciones
from backend.donaciones.service import DonacionService
from backend.inventario.service import InventarioService

class RegistrarDonacionOrquestador:

    def __init__(self, donacion_service: DonacionService, inventario_service: InventarioService):
        self.donacion_service = donacion_service
        self.inventario_service = inventario_service

    async def ejecutar(self, year: int, mes: int, datos: AgregarDonaciones) -> dict:
        
        respuesta = await self.donacion_service.registra_donacion(year, mes, datos)

        await self.inventario_service.registrar_ingreso(
            tipo_alimento = datos.tipo_alimento,
            cantidad = datos.cantidad,
            fecha_vencimiento = datos.fecha_vencimiento
        )

        return respuesta






