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

class EliminarDonacionOrquestador:

    def __init__(self, donacion_service: DonacionService, inventario_service: InventarioService):
        self.donacion_service = donacion_service
        self.inventario_service = inventario_service

    async def eliminar_especifica(self, year: int, mes: int, numero_semana: int, donacion_id: str) -> dict:

        donacion = await self.donacion_service.eliminar_donacion_especifica(year, mes, numero_semana, donacion_id)

        await self.inventario_service.registrar_salida(
            tipo_alimento=donacion.tipo_alimento, 
            cantidad=donacion.cantidad
        )

        return {"mensaje": f"Donacion de {donacion.cantidad} {donacion.tipo_alimento} eliminada y stock descontado exitosamente."}

    async def vaciar_semana(self, year: int, mes: int, numero_semana: int) -> dict:

        donaciones = await self.donacion_service.vaciar_donaciones_semana(year, mes, numero_semana)

        for donacion in donaciones:
            await self.inventario_service.registrar_salida(
                tipo_alimento=donacion.tipo_alimento, 
                cantidad=donacion.cantidad
            )
        
        return {"mensaje": f"Se eliminaron {len(donaciones)} donaciones y se desconto el stock de bodega."}





