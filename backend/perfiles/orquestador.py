from backend.perfiles.service import PerfilService
from backend.inventario.service import InventarioService
from fastapi import HTTPException
from datetime import datetime

class RegistrarRetiroOrquestador:

    def __init__(self, perfil_service: PerfilService, inventario_service: InventarioService):
        self.perfil_service = perfil_service
        self.inventario_service = inventario_service

    async def ejecutar(self, rut: str) -> dict:

        perfil = await self.perfil_service.repo.buscar_por_rut(rut)
        
        if not perfil or not perfil.activo:
            raise HTTPException(status_code=404, detail="Perfil no encontrado o inactivo.")

        fecha_actual = datetime.now()

        ya_retiro_este_mes = any(
            d.year == fecha_actual.year and d.month == fecha_actual.month
            for d in perfil.historial_retiros
        )
        
        if ya_retiro_este_mes:
            raise HTTPException(status_code=400, detail="Esta persona ya retiró alimentos este mes.")

        await self.inventario_service.registro_ticket_transaccion(rut)

        perfil.historial_retiros.append(fecha_actual.date())
        await self.perfil_service.repo.guardar(perfil)

        return {"mensaje" : f"Retiro mensual registrado exitosamente para {perfil.nombre}"}