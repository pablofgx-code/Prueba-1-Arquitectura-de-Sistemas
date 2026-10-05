import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from main import app
from backend.auth.dependencies import obtener_admin_actual
from backend.metricas.router import get_metricas_orquestador
from backend.metricas.orquestador import ObtenerMetricasOrquestador
from backend.metricas.schemas import DashboardMetrics, ResumenBodega

client = TestClient(app)

async def admin_mock():
    class Admin:
        nombre = "Admin"
        activo = True
    return Admin()

app.dependency_overrides[obtener_admin_actual] = admin_mock

class DummyPerfilService:
    async def contar_total_perfiles(self):
        return 150
        
    async def contar_retiros_mes_actual(self, year, month):
        return 200

class DummyDonacionService:
    async def contar_alimentos_mes_actual(self, year, month):
        return 500

class DummyInventarioService:
    async def contar_salidas_mes_actual(self, year, month):
        return 200

    async def obtener_resumen_agrupado(self):
        return [{"tipo_alimento": "Arroz", "cantidad_total": 300}]

@pytest.mark.asyncio
async def test_orquestador_metricas():
    orquestador = ObtenerMetricasOrquestador(
        DummyPerfilService(), 
        DummyDonacionService(), 
        DummyInventarioService()
    )
    resultado = await orquestador.ejecutar()

    assert resultado.total_personas_registradas == 150
    assert resultado.total_alimentos_ingresados_mes == 500
    assert resultado.total_alimentos_salidos_mes == 200
    assert len(resultado.inventario_actual) == 1
    assert resultado.inventario_actual[0].tipo_alimento == "Arroz"

def test_router_dashboard():
    class DummyOrquestador:
        async def ejecutar(self):
            return DashboardMetrics(
                total_personas_registradas=10,
                total_alimentos_ingresados_mes=50,
                total_alimentos_salidos_mes=20,
                inventario_actual=[ResumenBodega(tipo_alimento="Arroz", cantidad_total=30)]
            )

    app.dependency_overrides[get_metricas_orquestador] = lambda: DummyOrquestador()

    response = client.get("/api/metricas/dashboard")
    assert response.status_code == 200
    assert response.json()["total_personas_registradas"] == 10
    assert response.json()["total_alimentos_salidos_mes"] == 20