import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from beanie import PydanticObjectId
from fastapi import HTTPException
from datetime import timedelta

from main import app
from backend.auth import security
from backend.auth.dependencies import obtener_admin_actual
from backend.auth.repository import AdministradorRepository
from backend.auth.router import get_auth_service
from backend.auth.service import AuthService
from backend.auth.schemas import AdministradorCreate, LoginData, SolicitudRecuperacion

client = TestClient(app)

admin_mock = AsyncMock()
admin_mock.nombre = "Admin de Prueba"
admin_mock.activo = True
app.dependency_overrides[obtener_admin_actual] = lambda: admin_mock

def test_router_registrar_admin():
    mock_service = AsyncMock()
    mock_service.registrar_admin.return_value = {
        "id": PydanticObjectId("507f1f77bcf86cd799439011"),
        "email": "nuevo@iglesia.com",
        "nombre": "Nuevo Admin",
        "activo": True
    }
    app.dependency_overrides[get_auth_service] = lambda: mock_service

    payload = {"email": "nuevo@iglesia.com", "password": "password123", "nombre": "Nuevo Admin"}
    response = client.post("/api/auth/registro", json=payload)
    
    assert response.status_code == 201
    assert response.json()["email"] == "nuevo@iglesia.com"

def test_router_login():
    mock_service = AsyncMock()
    admin_respuesta = AsyncMock()
    admin_respuesta.nombre = "Super Admin"
    mock_service.autenticar_admin.return_value = admin_respuesta
    mock_service.generar_token_para_admin.return_value = "tokenfalso123"
    
    app.dependency_overrides[get_auth_service] = lambda: mock_service
    
    payload = {"email": "admin@test.com", "password": "password123"}
    response = client.post("/api/auth/login", json=payload)
    
    assert response.status_code == 200
    assert response.json()["admin"] == "Super Admin"
    assert "access_token" in response.headers.get("set-cookie", "")

def test_router_logout():
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert "hasta la proxima" in response.json()["mensaje"]

@pytest.mark.asyncio
async def test_servicio_registrar_admin_duplicado():
    mock_repo = AsyncMock()
    mock_repo.buscar_por_email.return_value = True 
    service = AuthService(mock_repo)
    
    dto = AdministradorCreate(email="existe@iglesia.com", password="password123", nombre="Juan")
    
    with pytest.raises(HTTPException) as exc_info:
        await service.registrar_admin(dto)
        
    assert exc_info.value.status_code == 400
    assert "ya esta registrado" in exc_info.value.detail

@pytest.mark.asyncio
async def test_servicio_login_correo_inexistente():
    mock_repo = AsyncMock()
    mock_repo.buscar_por_email.return_value = None 
    service = AuthService(mock_repo)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.autenticar_admin(LoginData(email="no@existe.com", password="123"))
        
    assert exc_info.value.status_code == 401
    assert "incorrectos" in exc_info.value.detail

@pytest.mark.asyncio
async def test_servicio_solicitar_recuperacion():
    mock_repo = AsyncMock()
    admin_falso = AsyncMock()
    admin_falso.email = "admin@iglesia.com"
    admin_falso.activo = True
    mock_repo.buscar_por_email.return_value = admin_falso
    
    service = AuthService(mock_repo)
    resultado = await service.solicitar_recuperacion(SolicitudRecuperacion(email="admin@iglesia.com"))
    
    assert "instrucciones" in resultado["mensaje"]

@pytest.mark.asyncio
@patch("backend.auth.service.Administrador")
async def test_servicio_registrar_admin_exitoso(mock_admin_class):
    mock_repo = AsyncMock()
    mock_repo.buscar_por_email.return_value = None 
    mock_admin_instance = AsyncMock()
    mock_admin_class.return_value = mock_admin_instance
    
    service = AuthService(mock_repo)
    dto = AdministradorCreate(email="excelente@iglesia.com", password="password123", nombre="Admin Genial")
    
    resultado = await service.registrar_admin(dto)
    
    assert resultado is not None
    assert mock_admin_class.called

def test_utilidades_seguridad():
    func_hash = getattr(security, "obtener_password_hash", getattr(security, "get_password_hash", None))
    func_verify = getattr(security, "verificar_password", getattr(security, "verify_password", None))
    func_token = getattr(security, "crear_token_acceso", getattr(security, "create_access_token", getattr(security, "crear_token", None)))
    
    if func_hash and func_verify:
        texto_plano = "secreto123"
        hash_generado = func_hash(texto_plano)
        
        assert hash_generado != texto_plano
        assert func_verify(texto_plano, hash_generado) is True
        assert func_verify("falso", hash_generado) is False
        
    if func_token:
        token = func_token(data={"sub": "correo@test.com"}, expires_delta=timedelta(minutes=15))
        assert isinstance(token, str)
        assert len(token) > 20

@pytest.mark.asyncio
async def test_servicio_login_exitoso():
    mock_repo = AsyncMock()
    admin_valido = AsyncMock()
    admin_valido.email = "admin@test.com"
    admin_valido.activo = True
    
    func_hash = getattr(security, "obtener_password_hash", getattr(security, "get_password_hash", None))
    if func_hash:
        admin_valido.hashed_password = func_hash("password123")
        mock_repo.buscar_por_email.return_value = admin_valido
        
        service = AuthService(mock_repo)
        resultado = await service.autenticar_admin(LoginData(email="admin@test.com", password="password123"))
        
        assert resultado is not None

def teardown_module():
    app.dependency_overrides.clear()