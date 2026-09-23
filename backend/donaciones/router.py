from fastapi import APIRouter, Depends
from backend.auth.dependencies import obtener_admin_actual
from backend.donaciones.schemas import InicializarMes, AgregarDonaciones, ResumenTotalMes, ModificarFecha
from backend.donaciones.models import MesDonacion
from backend.donaciones.service import DonacionService
from backend.donaciones.repository import DonacionRepository
from backend.donaciones.orquestador import RegistrarDonacionOrquestador, EliminarDonacionOrquestador
from backend.inventario.repository import InventarioRepository
from backend.inventario.service import InventarioService

router = APIRouter(
    prefix="/api/donaciones", 
    tags=["Donaciones"],
    dependencies=[Depends(obtener_admin_actual)]
)

def get_donacion_service() -> DonacionService:
    
    repo = DonacionRepository()
    
    return DonacionService(repo)

def get_registrar_donacion_orquestador(
    donacion_service: DonacionService = Depends(get_donacion_service)
) -> RegistrarDonacionOrquestador:

    inventario_repo = InventarioRepository()
    inventario_service = InventarioService(inventario_repo)

    return RegistrarDonacionOrquestador(donacion_service, inventario_service)

def get_eliminar_donacion_orquestador(
    donacion_service: DonacionService = Depends(get_donacion_service)
) -> EliminarDonacionOrquestador:
    inventario_repo = InventarioRepository()
    inventario_service = InventarioService(inventario_repo)
    return EliminarDonacionOrquestador(donacion_service, inventario_service)

@router.post("/", response_model=MesDonacion)
async def crear_mes(
    datos: InicializarMes,
    service: DonacionService = Depends(get_donacion_service)
):
    return await service.inicializar_nuevo_mes(datos)

@router.put("/{year}/{mes}")
async def agregar_alimento(
    year: int,
    mes: int,
    datos: AgregarDonaciones,
    orquestador: RegistrarDonacionOrquestador = Depends(get_registrar_donacion_orquestador)
):
    return await orquestador.ejecutar(year, mes, datos)

@router.get("/{year}/{mes}", response_model= MesDonacion)
async def ver_mes_completo(
    year: int,
    mes: int,
    service: DonacionService = Depends(get_donacion_service)
):
    return await service.obtener_mes_completo(year, mes)

@router.get("/{year}/{mes}/totales", response_model=ResumenTotalMes)
async def ver_totales(
    year: int,
    mes: int,
    service: DonacionService = Depends(get_donacion_service)
):
    return await service.obtener_total_mensual(year, mes)

@router.patch("/{year}/{mes}/fecha")
async def actualizar_fecha(
    year: int,
    mes: int,
    datos: ModificarFecha,
    service: DonacionService = Depends(get_donacion_service)
):
    return await service.modificar_fecha_creacion(year, mes, datos.nueva_fecha)

@router.post("/{year}/{mes}/semanas")
async def agregar_semana_extra(
    year: int,
    mes: int,
    service: DonacionService = Depends(get_donacion_service)
):
    return await service.agregar_semana(year, mes)

@router.delete("/{year}/{mes}/semana/{numero_semana}")
async def borrar_semana(
    year: int, 
    mes: int,
    numero_semana: int,
    service: DonacionService = Depends(get_donacion_service)
):
    return await service.eliminar_semana(year, mes, numero_semana)

@router.delete("/{year}/{mes}/semanas/{numero_semana}/donaciones/{donacion_id}")
async def borrar_donacion_especifica(
    year: int,
    mes: int,
    numero_semana: int, 
    donacion_id: str,
    orquestador: EliminarDonacionOrquestador = Depends(get_eliminar_donacion_orquestador)
):
    return await orquestador.eliminar_especifica(year, mes, numero_semana, donacion_id)

@router.delete("/{year}/{mes}/semanas/{numero_semana}/donaciones")
async def vaciar_donaciones_semana(
    year: int,
    mes: int,
    numero_semana: int, 
    orquestador: EliminarDonacionOrquestador = Depends(get_eliminar_donacion_orquestador)
):
    return await orquestador.vaciar_semana(year, mes, numero_semana)
