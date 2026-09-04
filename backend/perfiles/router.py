from fastapi import APIRouter, Depends, status
from typing import List
from backend.perfiles.schemas import PerfilCreate, PerfilResponse
from backend.perfiles.service import PerfilService
from backend.auth.dependencies import obtener_admin_actual

router = APIRouter(
    prefix="/api/perfiles", 
    tags=["Perfiles"],
    dependencies=[Depends(obtener_admin_actual)]
)

def get_perfil_service() -> PerfilService:
    return PerfilService()

@router.post("/", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
async def registrar_perfil(
    perfil: PerfilCreate,
    service: PerfilService = Depends(get_perfil_service)
):
    
    return await service.crear_perfil(perfil)

@router.get("/", response_model=List[PerfilResponse])
async def listar_perfiles(service: PerfilService = Depends(get_perfil_service)):
    
    return await service.obtener_todos()




