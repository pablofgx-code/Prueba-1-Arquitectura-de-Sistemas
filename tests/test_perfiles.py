import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from beanie import PydanticObjectId
from fastapi import HTTPException
from datetime import date, datetime

from main import app
from backend.auth.dependencies import obtener_admin_actual
from backend.perfiles.router import get_perfil_service, get_registrar_retiro_orquestador
from backend.perfiles.service import PerfilService
from backend.perfiles.schemas import PerfilCreate, SolicitudRetiro, ItemRetiro
from backend.perfiles.repository import PerfilRepository
from backend.perfiles.orquestador import RegistrarRetiroOrquestador

client = TestClient(app)

admin_mock = AsyncMock()
admin_mock.nombre = "Admin"
admin_mock.activo = True
app.dependency_overrides[obtener_admin_actual] = lambda: admin_mock

def test_router_listar_perfiles():
    mock_service = AsyncMock()
    mock_service.obtener_todos.return_value = [{
        "id": PydanticObjectId("507f1f77bcf86cd799439011"),
        "rut": "11111111-1", "nombre": "Juan", "apellido": "Perez",
        "fecha_nacimiento": date(1990, 1, 1), "edad": 34,
        "situacion_calle": False, "activo": True, "historial_retiros": []
    }]
    app.dependency_overrides[get_perfil_service] = lambda: mock_service

    response = client.get("/api/perfiles/listar")
    assert response.status_code == 200

def test_router_obtener_por_rut():
    mock_service = AsyncMock()
    mock_service.obtener_por_rut.return_value = {
        "id": PydanticObjectId("507f1f77bcf86cd799439011"),
        "rut": "22222222-2", "nombre": "Maria", "apellido": "Gomez",
        "fecha_nacimiento": date(1985, 5, 5), "edad": 40,
        "situacion_calle": True, "activo": True, "historial_retiros": []
    }
    app.dependency_overrides[get_perfil_service] = lambda: mock_service

    response = client.get("/api/perfiles/22222222-2")
    assert response.status_code == 200

def test_router_eliminar_perfil():
    mock_service = AsyncMock()
    mock_service.eliminar_perfil.return_value = {"mensaje": "Eliminado"}
    app.dependency_overrides[get_perfil_service] = lambda: mock_service

    response = client.delete("/api/perfiles/22222222-2")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_orquestador_retiro_exitoso():
    mock_perfil_service = AsyncMock()
    mock_inventario_service = AsyncMock()
    
    perfil_falso = AsyncMock()
    perfil_falso.activo = True
    perfil_falso.historial_retiros = []
    mock_perfil_service.repo.buscar_por_rut.return_value = perfil_falso
    
    orquestador = RegistrarRetiroOrquestador(mock_perfil_service, mock_inventario_service)
    datos = SolicitudRetiro(alimentos=[ItemRetiro(tipo_alimento="Arroz", cantidad=2)])
    
    res = await orquestador.ejecutar("11111111-1", datos)
    assert "exitosamente" in res["mensaje"]
    assert mock_inventario_service.registrar_salida.called

@pytest.mark.asyncio
@patch("backend.perfiles.service.Perfil")
async def test_servicio_crear_perfil_exitoso(mock_perfil_class):
    mock_repo = AsyncMock()
    mock_repo.buscar_por_rut.return_value = None 
    mock_perfil_class.return_value = AsyncMock()
    
    service = PerfilService(mock_repo)
    dto = PerfilCreate(
        nombre="Pedro", apellido="Pascal", rut="33333333-3", 
        fecha_nacimiento=date(1975, 4, 2), edad=49, situacion_calle=False
    )
    
    await service.crear_perfil(dto)
    assert mock_repo.insertar.called

@pytest.mark.asyncio
async def test_servicio_crear_perfil_duplicado():
    mock_repo = AsyncMock()
    perfil_existente = AsyncMock()
    perfil_existente.activo = True
    mock_repo.buscar_por_rut.return_value = perfil_existente 
    
    service = PerfilService(mock_repo)
    dto = PerfilCreate(
        nombre="Pedro", apellido="Pascal", rut="33333333-3", 
        fecha_nacimiento=date(1975, 4, 2), edad=49, situacion_calle=False
    )
    with pytest.raises(HTTPException):
        await service.crear_perfil(dto)

@pytest.mark.asyncio
async def test_servicio_resumen_agrupado():
    mock_repo = AsyncMock()
    perfil_falso = AsyncMock()
    perfil_falso.rut = "11111111-1"
    perfil_falso.nombre = "Juan"
    perfil_falso.apellido = "Perez"
    perfil_falso.activo = True
    perfil_falso.historial_retiros = [date(2026, 1, 15), date(2026, 2, 20)] 
    
    mock_repo.obtener_todos_historial.return_value = [perfil_falso]
    
    service = PerfilService(mock_repo)
    resumen = await service.obtener_resumen_agrupado_por_mes(2026)
    
    assert len(resumen[0]["personas"]) == 1
    assert len(resumen[1]["personas"]) == 1

@pytest.mark.asyncio
async def test_servicio_eliminar_perfil():
    mock_repo = AsyncMock()
    perfil_falso = AsyncMock()
    mock_repo.buscar_por_rut.return_value = perfil_falso
    
    service = PerfilService(mock_repo)
    await service.eliminar_perfil("11111111-1")
    assert mock_repo.eliminar.called

@pytest.mark.asyncio
@patch("backend.perfiles.repository.Perfil")
async def test_repository_perfiles(mock_perfil_model):
    repo = PerfilRepository()
    
    mock_perfil_model.find_one = AsyncMock()
    await repo.buscar_por_rut("11111111-1")
    assert mock_perfil_model.find_one.called
    
    perfil_mock = AsyncMock()
    perfil_mock.save = AsyncMock()
    await repo.eliminar(perfil_mock)
    assert perfil_mock.activo is False
    assert perfil_mock.save.called

def test_router_registrar_perfil():
    mock_service = AsyncMock()
    mock_service.crear_perfil.return_value = {
        "id": PydanticObjectId("507f1f77bcf86cd799439011"),
        "rut": "33333333-3", "nombre": "Pedro", "apellido": "Pascal",
        "fecha_nacimiento": date(1975, 4, 2), "edad": 49,
        "situacion_calle": False, "activo": True, "historial_retiros": []
    }
    app.dependency_overrides[get_perfil_service] = lambda: mock_service
    
    payload = {"nombre": "Pedro", "apellido": "Pascal", "rut": "33333333-3", "fecha_nacimiento": "1975-04-02", "edad": 49}
    response = client.post("/api/perfiles/registrar", json=payload)
    assert response.status_code == 201

def test_router_registrar_retiro():
    mock_orq = AsyncMock()
    mock_orq.ejecutar.return_value = {"mensaje": "Retiro registrado exitosamente"}
    app.dependency_overrides[get_registrar_retiro_orquestador] = lambda: mock_orq
    
    response = client.post("/api/perfiles/11111111-1/retiros", json={"alimentos": [{"tipo_alimento": "Arroz", "cantidad": 2}]})
    assert response.status_code == 200

def test_router_resumen_y_excel():
    mock_service = AsyncMock()
    from fastapi.responses import StreamingResponse
    import io
    
    mock_service.generar_reporte_excel.return_value = StreamingResponse(io.BytesIO(b"xls"), status_code=200)
    mock_service.obtener_resumen_agrupado_por_mes.return_value = []
    app.dependency_overrides[get_perfil_service] = lambda: mock_service
    
    res_excel = client.get("/api/perfiles/reporte/excel")
    assert res_excel.status_code == 200
    
    res_resumen = client.get("/api/perfiles/resumen/retiros/2026")
    assert res_resumen.status_code == 200

@pytest.mark.asyncio
async def test_orquestador_perfil_no_existe_o_inactivo():
    mock_perfil_service = AsyncMock()
    mock_inventario_service = AsyncMock()
    mock_perfil_service.repo.buscar_por_rut.return_value = None 
    
    orq = RegistrarRetiroOrquestador(mock_perfil_service, mock_inventario_service)
    with pytest.raises(HTTPException) as exc:
        await orq.ejecutar("11", SolicitudRetiro(alimentos=[]))
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_orquestador_retiro_duplicado():
    mock_perfil_service = AsyncMock()
    mock_inventario_service = AsyncMock()
    perfil = AsyncMock()
    perfil.activo = True
    perfil.historial_retiros = [datetime.now().date()] 
    mock_perfil_service.repo.buscar_por_rut.return_value = perfil
    
    orq = RegistrarRetiroOrquestador(mock_perfil_service, mock_inventario_service)
    with pytest.raises(HTTPException) as exc:
        await orq.ejecutar("11", SolicitudRetiro(alimentos=[]))
    assert exc.value.status_code == 400

@pytest.mark.asyncio
@patch("backend.perfiles.repository.Perfil")
async def test_repository_metodos_restantes(mock_perfil_model):
    repo = PerfilRepository()
    perfil = AsyncMock()
    perfil.insert = AsyncMock()
    perfil.save = AsyncMock()
    
    await repo.insertar(perfil)
    assert perfil.insert.called
    
    await repo.guardar(perfil)
    assert perfil.save.called
    
    mock_perfil_model.find.return_value.to_list = AsyncMock(return_value=[])
    await repo.obtener_todos()
    assert mock_perfil_model.find.called
    
    mock_perfil_model.find_all.return_value.to_list = AsyncMock(return_value=[])
    await repo.obtener_todos_historial()
    assert mock_perfil_model.find_all.called

@pytest.mark.asyncio
async def test_servicio_obtener_y_contar_y_eliminar():
    repo = AsyncMock()
    repo.buscar_por_rut.return_value = None 
    repo.obtener_todos.return_value = [1, 2, 3]
    
    service = PerfilService(repo)
    
    assert await service.contar_total_perfiles() == 3
    assert len(await service.obtener_todos()) == 3
    
    with pytest.raises(HTTPException) as exc1:
        await service.eliminar_perfil("xx")
    assert exc1.value.status_code == 404
    
    with pytest.raises(HTTPException) as exc2:
        await service.obtener_por_rut("xx")
    assert exc2.value.status_code == 404

@pytest.mark.asyncio
async def test_servicio_crear_perfil_inactivo():
    repo = AsyncMock()
    perfil_inactivo = AsyncMock()
    perfil_inactivo.activo = False
    repo.buscar_por_rut.return_value = perfil_inactivo
    
    service = PerfilService(repo)
    dto = PerfilCreate(nombre="Juan", apellido="Perez", rut="12345678-9", fecha_nacimiento=date(2000,1,1), edad=20)
    
    with pytest.raises(HTTPException) as exc:
        await service.crear_perfil(dto)
    assert "reactivar" in exc.value.detail
