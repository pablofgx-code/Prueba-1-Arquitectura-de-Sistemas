import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import date
from pydantic import TypeAdapter
from beanie import PydanticObjectId

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from datetime import date

from main import app
from backend.donaciones.router import get_donacion_service
from backend.donaciones.schemas import ResumenTotalMes
from backend.donaciones.models import MesDonacion
from backend.auth.dependencies import obtener_admin_actual
from backend.auth.router import get_auth_service
from backend.auth.models import Administrador
from backend.perfiles.router import get_perfil_service
from backend.perfiles.service import PerfilService
from backend.inventario.router import get_inventario_service
from backend.inventario.service import InventarioService
from backend.metricas.router import get_metricas_orquestador
from backend.metricas.schemas import DashboardMetrics
from backend.perfiles.models import Perfil

client = TestClient(app)


app.dependency_overrides[obtener_admin_actual] = lambda: {"nombre": "Admin", "activo": True}

def test_ver_bodega_completa():
    mock_repo = AsyncMock()
    mock_repo.obtener_todo.return_value = []
    
    mock_service = InventarioService(mock_repo)
    app.dependency_overrides[get_inventario_service] = lambda: mock_service

    response = client.get("/api/inventario/")
    
    assert response.status_code == 200
    assert response.json() == []

def test_listar_perfiles():
    mock_repo = AsyncMock()
    
    perfil_dict = {
        "id": PydanticObjectId("507f1f77bcf86cd799439011"),
        "nombre": "Juan",
        "apellido": "Perez",
        "rut": "11111111-1",
        "contacto": "911111111",
        "fecha_nacimiento": date(1990, 1, 1),
        "edad": 36,
        "situacion_calle": False,
        "motivo_situacion": None,
        "historial_retiros": [],
        "activo": True
    }
    
    mock_repo.obtener_todos.return_value = [perfil_dict]
    
    mock_service = PerfilService(mock_repo)
    app.dependency_overrides[get_perfil_service] = lambda: mock_service

    response = client.get("/api/perfiles/listar")
    assert response.status_code == 200
    assert response.json()[0]["rut"] == "11111111-1"

def test_crear_perfil_error_duplicado():
    mock_repo = AsyncMock()
    perfil_falso = AsyncMock()
    perfil_falso.activo = True
    mock_repo.buscar_por_rut.return_value = perfil_falso
    
    mock_service = PerfilService(mock_repo)
    app.dependency_overrides[get_perfil_service] = lambda: mock_service

    payload = {
        "nombre": "Pedro", "apellido": "Gomez", "rut": "11111111-1",
        "fecha_nacimiento": "1990-01-01", "edad": 30
    }
    response = client.post("/api/perfiles/registrar", json=payload)
    
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"]

def test_ver_metricas():
    mock_orquestador = AsyncMock()
    mock_orquestador.ejecutar.return_value = DashboardMetrics(
        total_personas_registradas=50,
        total_alimentos_ingresados_mes=100,
        total_alimentos_salidos_mes=20,
        inventario_actual=[]
    )
    app.dependency_overrides[get_metricas_orquestador] = lambda: mock_orquestador

    response = client.get("/api/metricas/dashboard")
    
    assert response.status_code == 200
    assert response.json()["total_personas_registradas"] == 50

def teardown_module():
    app.dependency_overrides.clear()


def test_ver_totales_donaciones():
    mock_service = AsyncMock()
    resumen_falso = ResumenTotalMes(
        year=2026,
        mes=9,
        total_alimentos_donados=50
    )
    mock_service.obtener_total_mensual.return_value = resumen_falso
    app.dependency_overrides[get_donacion_service] = lambda: mock_service

    response = client.get("/api/donaciones/2026/9/totales")
    assert response.status_code == 200
    assert response.json()["total_alimentos_donados"] == 50

def test_registrar_administrador():
    mock_auth_service = AsyncMock()
    
    admin_falso = AsyncMock()
    admin_falso.id = PydanticObjectId("507f1f77bcf86cd799439011")
    admin_falso.email = "test@iglesia.com"
    admin_falso.nombre = "Pastor Test"
    admin_falso.activo = True
    
    mock_auth_service.registrar_admin.return_value = admin_falso
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    payload = {
        "email": "test@iglesia.com",
        "password": "password123",
        "nombre": "Pastor Test"
    }
    response = client.post("/api/auth/registro", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "test@iglesia.com"