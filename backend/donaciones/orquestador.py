from backend.donaciones.schemas import AgregarDonaciones
from backend.donaciones.models import DonacionAlimento
from backend.donaciones.service import DonacionService
from backend.inventario.service import InventarioService
from typing import List
from fastapi import HTTPException

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

        mes_doc = await self.donacion_service.obtener_mes_completo(year, mes)
        semana = next((s for s in mes_doc.semanas if s.numero_semana == numero_semana), None)
        if not semana:
            raise HTTPException(status_code=404, detail="Semana no encontrada")

        donacion = next((d for d in semana.donaciones if d.id == donacion_id), None)
        if not donacion:
            raise HTTPException(status_code=404, detail="La donacion no existe")
        
        await self.inventario_service.revertir_ingreso(
            tipo_alimento = donacion.tipo_alimento, 
            cantidad = donacion.cantidad,
            fecha_vencimiento = donacion.fecha_vencimiento
        )

        await self.donacion_service.eliminar_donacion_especifica(year, mes, numero_semana, donacion_id)
        
        return {"mensaje": f"Donacion de {donacion.cantidad} {donacion.tipo_alimento} eliminada y stock revertido exitosamente."}

    async def vaciar_semana(self, year: int, mes: int, numero_semana: int) -> dict:

        mes_doc = await self.donacion_service.obtener_mes_completo(year, mes)
        semana = next((s for s in mes_doc.semanas if s.numero_semana == numero_semana), None)
        
        if not semana or not semana.donaciones:
            return {"mensaje": "La semana ya estaba vacía."}
            
        donaciones = list(semana.donaciones)

        for donacion in donaciones:
            await self.inventario_service.revertir_ingreso(
                tipo_alimento=donacion.tipo_alimento, 
                cantidad=donacion.cantidad,
                fecha_vencimiento=donacion.fecha_vencimiento
            )
        await self.donacion_service.vaciar_donaciones_semana(year, mes, numero_semana)
        
        return {"mensaje": f"Se eliminaron {len(donaciones)} donaciones y se revirtió el stock de bodega."}





