from fastapi import APIRouter, Depends, status
from typing import List
from fastapi.responses import StreamingResponse
from backend.perfiles.schemas import PerfilCreate, PerfilResponse, SolicitudRetiro
from backend.perfiles.service import PerfilService
from backend.auth.dependencies import obtener_admin_actual
from backend.perfiles.repository import PerfilRepository
from backend.perfiles.orquestador import RegistrarRetiroOrquestador
from backend.inventario.repository import InventarioRepository
from backend.inventario.service import InventarioService

router = APIRouter(
    prefix="/api/perfiles", 
    tags=["Perfiles"],
    dependencies=[Depends(obtener_admin_actual)]
)

def get_perfil_service() -> PerfilService:
    repo = PerfilRepository()
    return PerfilService(repo)

def get_registrar_retiro_orquestador(
    perfil_service: PerfilService = Depends(get_perfil_service)
) -> RegistrarRetiroOrquestador:
    
    inventario_repo = InventarioRepository()
    inventario_service = InventarioService(inventario_repo)

    return RegistrarRetiroOrquestador(perfil_service, inventario_service)

@router.post("/registrar", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
async def registrar_perfil(
    perfil: PerfilCreate,
    service: PerfilService = Depends(get_perfil_service)
):
    return await service.crear_perfil(perfil)

@router.get("/listar", response_model=List[PerfilResponse])
async def listar_perfiles(
    service: PerfilService = Depends(get_perfil_service)
):
    return await service.obtener_todos()

@router.post("/{rut}/retiros")
async def registrar_retiro_manual(
    rut: str,
    datos: SolicitudRetiro,
    orquestador: RegistrarRetiroOrquestador = Depends(get_registrar_retiro_orquestador)
):
    return await orquestador.ejecutar(rut, datos)

@router.get("/reporte/excel", response_class=StreamingResponse)
async def descargar_reporte_excel(
    service: PerfilService = Depends(get_perfil_service)
):
    return await service.generar_reporte_excel()

@router.get("/resumen/retiros/{year}")
async def ver_resumen_anual_retiros(
    year: int,
    service: PerfilService = Depends(get_perfil_service)
):
    return await service.obtener_resumen_agrupado_por_mes(year)

@router.get("/{rut}", response_model=PerfilResponse)
async def obtener_perfil_por_rut(
    rut: str,
    service: PerfilService = Depends(get_perfil_service)
):
    return await service.obtener_por_rut(rut)

@router.delete("/{rut}")
async def eliminar_perfil_beneficiario(
    rut: str,
    service: PerfilService = Depends(get_perfil_service)
):
    return await service.eliminar_perfil(rut)