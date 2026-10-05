from fastapi import HTTPException, status
from backend.inventario.models import LotePerecible, RegistroSalida
from backend.inventario.repository import InventarioRepository
from datetime import datetime

class InventarioService:

    def __init__(self, repo: InventarioRepository):
        self.repo = repo

    async def obtener_bodega_completa(self):
        return await self.repo.obtener_todo()

    async def registrar_ingreso(self, tipo_alimento: str, cantidad: int) -> LotePerecible:
        lote_existente = await self.repo.buscar_lote_especifico(tipo_alimento)

        if lote_existente:
            lote_existente.cantidad_disponible += cantidad
            return await self.repo.guardar(lote_existente)
        
        nuevo_lote = LotePerecible(
            tipo_alimento = tipo_alimento.capitalize(),
            cantidad_disponible = cantidad
        )
        return await self.repo.insert(nuevo_lote)
        
    async def revertir_ingreso(self, tipo_alimento: str, cantidad: int):
        lote = await self.repo.buscar_lote_especifico(tipo_alimento)
        
        if not lote or lote.cantidad_disponible < cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente para revertir la donacion de {tipo_alimento}."
            )
        
        lote.cantidad_disponible -= cantidad
        await self.repo.guardar(lote)

    async def obtener_resumen_agrupado(self) -> list:
        
        lotes = await self.repo.obtener_todo()
        
        resumen = {}

        for lote in lotes:
            if lote.cantidad_disponible > 0:
                if lote.tipo_alimento in resumen:
                    resumen[lote.tipo_alimento] += lote.cantidad_disponible
                else:
                    resumen[lote.tipo_alimento] = lote.cantidad_disponible
        
        return [{"tipo_alimento" : nombre, "cantidad_total" : total} for nombre, total in resumen.items()]

    async def registro_ticket_transaccion(self, rut: str) -> None:
        ticket = RegistroSalida(
            fecha = datetime.now(),
            rut_beneficiario = rut
        )
        await self.repo.guardar_ticket_salida(ticket)

    async def contar_salidas_mes_actual(self, year: int, mes: int) -> int:
        return await self.repo.sumar_salidas_del_mes(year, mes)

    async def vaciar_bodega(self) -> None:

        await LotePerecible.delete_all()


