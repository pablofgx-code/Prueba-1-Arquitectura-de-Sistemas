from typing import List
from backend.inventario.models import LotePerecible, RegistroSalida

class InventarioRepository:

    async def insert(self, item: LotePerecible) -> LotePerecible:
        await item.insert()
        return item

    async def guardar(self, item: LotePerecible) -> LotePerecible:
        await item.save()
        return item

    async def obtener_todo(self) -> List[LotePerecible]:
        return await LotePerecible.find(
            LotePerecible.cantidad_disponible > 0
        ).to_list()

    async def guardar_ticket_salida(self, ticket: RegistroSalida) -> RegistroSalida:
        await ticket.insert()
        return ticket

    async def buscar_lote_especifico(self, tipo_alimento: str) -> LotePerecible | None:
        return await LotePerecible.find_one(
            LotePerecible.tipo_alimento == tipo_alimento.capitalize()
        )

    async def sumar_salidas_del_mes(self, year: int, mes: int) -> int:
        pipeline = [
            {"$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$year": "$fecha"}, year]},
                        {"$eq": [{"$month": "$fecha"}, mes]}
                    ]
                }
            }}
        ]
        resultados = await RegistroSalida.aggregate(pipeline).to_list()
        return len(resultados)