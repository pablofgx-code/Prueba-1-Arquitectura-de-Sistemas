from fastapi import HTTPException, status
from backend.inventario.models import ItemInventario
from backend.inventario.repository import InventarioRepository

class InventarioService:

    def __init__(self, repo: InventarioRepository):
        self.repo = repo

    async def obtener_bodega_completa(self):
        return await self.repo.obtener_todo()

    async def modificar_stock(self, tipo_alimento: str, cantidad: int, es_ingreso: bool) -> ItemInventario:
        item = await self.repo.buscar_por_alimento(tipo_alimento)

        if not item and es_ingreso:
            nuevo_item = ItemInventario(tipo_alimento = tipo_alimento.capitalize(), cantidad_disponible = cantidad)
            return await self.repo.insertar(nuevo_item)

        if not item and not es_ingreso:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"No hay registros de {tipo_alimento} en la bodega."
            )

        if es_ingreso:
            item.cantidad_disponible += cantidad
        else:
            if item.cantidad_disponible < cantidad:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = f"Stock insuficiente para {item.tipo_alimento}. Disponible: {item.cantidad_disponible}." 
                )
        
        return await self.repo.guardar(item)

        




