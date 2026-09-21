from backend.perfiles.service import PerfilService
from backend.inventario.service import InventarioService
from backend.perfiles.schemas import SolicitudRetiro

class RegistrarRetiroOrquestador:

    def __init__(self, perfil_service: PerfilService, inventario_service: InventarioService):
        self.perfil_service = perfil_service
        self.inventario_service = inventario_service

    async def ejecutar(self, rut: str, datos: SolicitudRetiro) -> dict:

        for item in datos.alimentos:
            await self.inventario_service.registrar_salida(
                tipo_alimento = item.tipo_alimento,
                cantidad_requerida = item.cantidad
            )

        await self.inventario_service.registro_ticket_transaccion(rut, datos.alimentos)

        return await self.perfil_service.registrar_retiro(rut)







