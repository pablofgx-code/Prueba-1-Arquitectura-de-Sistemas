from fastapi import HTTPException, status
from backend.inventario.models import LotePerecible, ItemLlevado, RegistroSalida
from backend.inventario.repository import InventarioRepository
from datetime import date, datetime

class InventarioService:

    def __init__(self, repo: InventarioRepository):
        self.repo = repo

    async def obtener_bodega_completa(self):
        return await self.repo.obtener_todo()

    async def registrar_ingreso(self, tipo_alimento: str, cantidad: int, fecha_vencimiento: date) -> LotePerecible:

        nuevo_lote = LotePerecible(
            tipo_alimento = tipo_alimento.capitalize(),
            cantidad_disponible = cantidad,
            fecha_vencimiento = fecha_vencimiento
        )
        return await self.repo.insert(nuevo_lote)

    async def registrar_salida(self, tipo_alimento: str, cantidad_requerida: int):

        lotes = await self.repo.buscar_lotes_disponibles(tipo_alimento)

        total_disponible = sum(lote.cantidad_disponible for lote in lotes)

        if total_disponible < cantidad_requerida:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"Stock insuficiente de {tipo_alimento}. Solicitado: {cantidad_requerida}, Disponible: {total_disponible}."
            )

        cantidad_por_descontar = cantidad_requerida

        for lote in lotes:
            if cantidad_por_descontar == 0:
                break

            if lote.cantidad_disponible <= cantidad_por_descontar:
                cantidad_por_descontar -= lote.cantidad_disponible
                lote.cantidad_disponible = 0
            else:
                lote.cantidad_disponible -= cantidad_por_descontar
                cantidad_por_descontar = 0

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
        
        return [{"nombre" : nombre, "cantidad_total" : total} for nombre, total in resumen.items()]

    async def registro_ticket_transaccion(self, rut: str, alimentos: list) -> None:

        items = [ItemLlevado(tipo_alimento = alimento.tipo_alimento, cantidad = alimento.cantidad) for alimento in alimentos]
        
        ticket = RegistroSalida(
            fecha = datetime.now(),
            rut_beneficiario = rut,
            alimentos_entregados = items
        )
        
        await self.repo.guardar_ticket_salida(ticket)

    async def contar_salidas_mes_actual(self, year: int, mes: int) -> int:

        return await self.repo.sumar_salidas_del_mes(year, mes)


