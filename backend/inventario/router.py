from fastapi import APIRouter, Depends
from typing import List
from backend.auth.dependencies import obtener_admin_actual
from backend.inventario.schemas import LotePerecibleResponse
from backend.inventario.service import InventarioService
from backend.inventario.repository import InventarioRepository

router = APIRouter(
    prefix = "/api/inventario",
    tags = ["Inventario Bodega"],
    dependencies = [Depends(obtener_admin_actual)]
)

def get_inventario_service() -> InventarioService:
    repo = InventarioRepository()
    return InventarioService(repo)

@router.get("/", response_model = List[LotePerecibleResponse])
async def ver_bodega_completa(
    service: InventarioService = Depends(get_inventario_service)
):
    return await service.obtener_bodega_completa()




