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
from backend.inventario.models import LotePerecible, RegistroSalida
from backend.inventario.router import get_inventario_service
from backend.inventario.service import InventarioService
from backend.inventario.repository import InventarioRepository

client = TestClient(app)

admin_mock = AsyncMock()
admin_mock.nombre = "Admin"
admin_mock.activo = True
app.dependency_overrides[obtener_admin_actual] = lambda: admin_mock

def test_router_ver_bodega():
    mock_service = AsyncMock()
    mock_service.obtener_bodega_completa.return_value = [
        {
            "id": PydanticObjectId("507f1f77bcf86cd799439011"), 
            "tipo_alimento": "Arroz", 
            "cantidad_disponible": 10, 
            "fecha_vencimiento": date(2025, 1, 1)
        }
    ]
    app.dependency_overrides[get_inventario_service] = lambda: mock_service
    
    response = client.get("/api/inventario/")
    assert response.status_code == 200
    assert response.json()[0]["tipo_alimento"] == "Arroz"

@pytest.mark.asyncio
@patch("backend.inventario.service.LotePerecible")
async def test_servicio_registrar_ingreso(mock_lote_class):
    repo = AsyncMock()
    service = InventarioService(repo)
    
    repo.buscar_lote_especifico.return_value = None
    mock_lote_class.return_value = AsyncMock()
    await service.registrar_ingreso("Fideos", 10, date(2025, 1, 1))
    assert repo.insert.called
    
    lote_existente = AsyncMock()
    lote_existente.cantidad_disponible = 5
    repo.buscar_lote_especifico.return_value = lote_existente
    await service.registrar_ingreso("Fideos", 5, date(2025, 1, 1))
    assert lote_existente.cantidad_disponible == 10
    assert repo.guardar.called

@pytest.mark.asyncio
async def test_servicio_registrar_salida():
    repo = AsyncMock()
    service = InventarioService(repo)
    
    lote1 = AsyncMock()
    lote1.cantidad_disponible = 5
    
    repo.buscar_lotes_disponibles.return_value = [lote1]
    with pytest.raises(HTTPException) as exc:
        await service.registrar_salida("Arroz", 10)
    assert exc.value.status_code == 400
    assert "insuficiente" in exc.value.detail
    
    lote2 = AsyncMock()
    lote2.cantidad_disponible = 10
    repo.buscar_lotes_disponibles.return_value = [lote1, lote2] 
    
    await service.registrar_salida("Arroz", 12)
    assert lote1.cantidad_disponible == 0
    assert lote2.cantidad_disponible == 3
    assert repo.guardar.call_count == 2

@pytest.mark.asyncio
async def test_servicio_revertir_ingreso():
    repo = AsyncMock()
    service = InventarioService(repo)
    
    lote1 = AsyncMock()
    lote1.cantidad_disponible = 5
    repo.buscar_lotes_por_fecha.return_value = [lote1]
    
    with pytest.raises(HTTPException) as exc:
        await service.revertir_ingreso("Leche", 10, date(2025,1,1))
    assert exc.value.status_code == 400
        
    await service.revertir_ingreso("Leche", 5, date(2025,1,1))
    assert lote1.cantidad_disponible == 0
    assert repo.guardar.called

@pytest.mark.asyncio
@patch("backend.inventario.service.RegistroSalida")
@patch("backend.inventario.service.ItemLlevado")
async def test_servicio_utilidades_extras(mock_item, mock_registro):
    repo = AsyncMock()
    service = InventarioService(repo)
    
    lote = AsyncMock()
    lote.tipo_alimento = "Azucar"
    lote.cantidad_disponible = 20
    repo.obtener_todo.return_value = [lote]
    resumen = await service.obtener_resumen_agrupado()
    assert resumen[0]["tipo_alimento"] == "Azucar"
    assert resumen[0]["cantidad_total"] == 20
    
    repo.sumar_salidas_del_mes.return_value = 100
    salidas = await service.contar_salidas_mes_actual(2026, 9)
    assert salidas == 100
    
    alimento_mock = AsyncMock()
    alimento_mock.tipo_alimento = "Pan"
    alimento_mock.cantidad = 2
    mock_registro.return_value = AsyncMock()
    
    await service.registro_ticket_transaccion("11111111-1", [alimento_mock])
    assert repo.guardar_ticket_salida.called

@pytest.mark.asyncio
async def test_inventario_repository_basicos():
    repo = InventarioRepository()
    
    lote_falso = AsyncMock()
    lote_falso.insert = AsyncMock()
    await repo.insert(lote_falso)
    assert lote_falso.insert.called
    
    lote_falso.save = AsyncMock()
    await repo.guardar(lote_falso)
    assert lote_falso.save.called
    
    ticket_falso = AsyncMock()
    ticket_falso.insert = AsyncMock()
    await repo.guardar_ticket_salida(ticket_falso)
    assert ticket_falso.insert.called

def test_cobertura_router_dependencia():
    from backend.inventario.router import get_inventario_service
    servicio = get_inventario_service()
    assert servicio is not None
