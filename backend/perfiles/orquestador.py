from backend.perfiles.service import PerfilService
from backend.inventario.service import InventarioService
from backend.perfiles.schemas import SolicitudRetiro
from fastapi import HTTPException
from datetime import datetime

class RegistrarRetiroOrquestador:

    def __init__(self, perfil_service: PerfilService, inventario_service: InventarioService):
        self.perfil_service = perfil_service
        self.inventario_service = inventario_service

    async def ejecutar(self, rut: str, datos: SolicitudRetiro) -> dict:

        perfil = await self.perfil_service.repo.buscar_por_rut(rut)
        
        if not perfil or not perfil.activo:
            raise HTTPException(status_code=404, detail="Perfil no encontrado o inactivo.")

        fecha_actual = datetime.now().date()
        if fecha_actual in perfil.historial_retiros:
            raise HTTPException(status_code=400, detail="Esta persona ya tiene registrado un retiro el dia de hoy.")

        for item in datos.alimentos:
            await self.inventario_service.registrar_salida(
                tipo_alimento = item.tipo_alimento,
                cantidad_requerida = item.cantidad
            )

        await self.inventario_service.registro_ticket_transaccion(rut, datos.alimentos)

        perfil.historial_retiros.append(fecha_actual)
        
        await self.perfil_service.repo.guardar(perfil)

        return {"mensaje" : f"Retiro registrado exitosamente para {perfil.nombre}"}







