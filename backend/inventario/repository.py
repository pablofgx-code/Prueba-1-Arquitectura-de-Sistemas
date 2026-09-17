from typing import List
from backend.inventario.models import ItemInventario

class InventarioRepository:

    async def buscar_por_alimento(self, tipo_alimento: str) -> ItemInventario | None:

        return await ItemInventario.find_one({"tipo_alimento" : {"$regex" : f"^{tipo_alimento}$", "$options" : "i"}})

    async def insert(self, item: ItemInventario) -> ItemInventario:
        
        await item.insert()
        
        return item

    async def guardar(self, item: ItemInventario) -> ItemInventario:
        
        await item.save()
        
        return item

    async def obtener_todo(self) -> List[ItemInventario]:
        
        return await ItemInventario.find_all().to_list()





