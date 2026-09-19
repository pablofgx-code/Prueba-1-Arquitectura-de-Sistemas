from typing import List
from backend.inventario.models import LotePerecible

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





