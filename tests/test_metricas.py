import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from main import app
from backend.auth.dependencies import obtener_admin_actual
from backend.metricas.router import get_metricas_orquestador
from backend.metricas.orquestador import ObtenerMetricasOrquestador
from backend.metricas.schemas import DashboardMetrics, ResumenBodega

client = TestClient(app)

admin_mock = AsyncMock()
admin_mock.nombre = "Admin"
admin_mock.activo = True
app.dependency_overrides[obtener_admin_actual] = lambda: admin_mock

@pytest.mark.asyncio
async def test_orquestador_metricas():
    mock_perfil = AsyncMock()
    mock_perfil.contar_total_perfiles.return_value = 150

    mock_donacion = AsyncMock()
    mock_donacion.contar_alimentos_mes_actual.return_value = 500

    mock_inventario = AsyncMock()
    mock_inventario.contar_salidas_mes_actual.return_value = 200
    mock_inventario.obtener_resumen_agrupado.return_value = [{"tipo_alimento": "Arroz", "cantidad_total": 300}]

    orquestador = ObtenerMetricasOrquestador(mock_perfil, mock_donacion, mock_inventario)
    resultado = await orquestador.ejecutar()

    assert resultado.total_personas_registradas == 150
    assert resultado.total_alimentos_ingresados_mes == 500
    assert resultado.total_alimentos_salidos_mes == 200
    assert len(resultado.inventario_actual) == 1

def test_router_dashboard():
    mock_orq = AsyncMock()
    mock_orq.ejecutar.return_value = DashboardMetrics(
        total_personas_registradas=10,
        total_alimentos_ingresados_mes=50,
        total_alimentos_salidos_mes=20,
        inventario_actual=[ResumenBodega(tipo_alimento="Arroz", cantidad_total=30)]
    )
    app.dependency_overrides[get_metricas_orquestador] = lambda: mock_orq

    response = client.get("/api/metricas/dashboard")
    assert response.status_code == 200
    assert response.json()["total_personas_registradas"] == 10
