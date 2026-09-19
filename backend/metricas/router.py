from fastapi import APIRouter, Depends
from backend.auth.dependencies import obtener_admin_actual
from backend.metricas.schemas import DashboardMetrics
from backend.metricas.orquestador import ObtenerMetricasOrquestador
from backend.perfiles.router import get_perfil_service
from backend.donaciones.router import get_donacion_service

router = APIRouter(
    prefix = "/api/metricas",
    tag = ["Metricas Dashboard"],
    dependencies = [Depends(obtener_admin_actual)]
)

def get_metricas_orquestador(
    perfil_service = Depends(get_perfil_service),
    donacion_service = Depends(get_donacion_service)
) -> ObtenerMetricasOrquestador:
    return ObtenerMetricasOrquestador(perfil_service, donacion_service)

@router.get("/dashboard", response_model = DashboardMetrics)
async def ver_metricas_dashboard(
    orquestador: ObtenerMetricasOrquestador = Depends(get_metricas_orquestador)
):
    return await orquestador.ejecutar()



