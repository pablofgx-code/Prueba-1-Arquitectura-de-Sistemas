from typing import List
from backend.inventario.models import LotePerecible, RegistroSalida

class InventarioRepository:

    async def buscar_lotes_disponibles(self, tipo_alimento: str) -> List[LotePerecible]:

        return await LotePerecible.find(
            LotePerecible.tipo_alimento == tipo_alimento.capitalize(),
            LotePerecible.cantidad_disponible > 0
        ).sort(+LotePerecible.fecha_vencimiento).to_list()

    async def insert(self, item: LotePerecible) -> LotePerecible:
        
        await item.insert()
        
        return item

    async def guardar(self, item: LotePerecible) -> LotePerecible:
        
        await item.save()
        
        return item

    async def obtener_todo(self) -> List[LotePerecible]:
        
        return await LotePerecible.find_all().to_list()

    async def guardar_ticket_salida(self, ticket: RegistroSalida) -> RegistroSalida:
        await ticket.insert()
        return ticket

    async def sumar_salidas_del_mes(self, year: int, mes: int) -> int:
        pipeline = [
            {"$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$year": "$fecha"}, year]},
                        {"$eq": [{"$month": "$fecha"}, mes]}
                    ]
                }
            }},
            {"$unwind": "$alimentos_entregados"},
            {"$group": {
                "_id": None,
                "total_kilos": {"$sum": "$alimentos_entregados.cantidad"}
            }}
        ]

        resultado = await RegistroSalida.aggregate(pipeline).to_list()
        return resultado[0]["total_kilos"] if resultado else 0
 
