import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from datetime import date

from main import app
from backend.auth.dependencies import obtener_admin_actual
from backend.donaciones.router import get_donacion_service, get_registrar_donacion_orquestador, get_eliminar_donacion_orquestador
from backend.donaciones.service import DonacionService
from backend.donaciones.schemas import InicializarMes, AgregarDonaciones
from backend.donaciones.orquestador import EliminarDonacionOrquestador
from backend.donaciones.repository import DonacionRepository

client = TestClient(app)

admin_mock = AsyncMock()
admin_mock.nombre = "Admin"
admin_mock.activo = True
app.dependency_overrides[obtener_admin_actual] = lambda: admin_mock

@pytest.mark.asyncio
async def test_servicio_metodos_principales():
    repo = AsyncMock()
    
    mes_falso = AsyncMock()
    mes_falso.year = 2026
    mes_falso.mes = 10
    
    semana_falsa = AsyncMock()
    semana_falsa.numero_semana = 1
    
    donacion_falsa = AsyncMock()
    donacion_falsa.id = "id-123"
    donacion_falsa.cantidad = 5
    semana_falsa.donaciones = [donacion_falsa]
    mes_falso.semanas = [semana_falsa]
    
    repo.buscar_por_mes.return_value = mes_falso
    service = DonacionService(repo)
    
    datos_donacion = AgregarDonaciones(numero_semana=1, tipo_alimento="Arroz", cantidad=10, fecha_vencimiento=date(2027,1,1))
    await service.registra_donacion(2026, 10, datos_donacion)
    assert repo.guardar.called
    
    res_total = await service.obtener_total_mensual(2026, 10)
    assert res_total.total_alimentos_donados >= 5
    
    await service.modificar_fecha_creacion(2026, 10, "12/12/2026")
    assert mes_falso.fecha_creacion == "12/12/2026"
    
    mes_falso.semanas = [semana_falsa]
    await service.agregar_semana(2026, 10)
    
    semana_vacia = AsyncMock()
    semana_vacia.numero_semana = 2
    semana_vacia.donaciones = []
    mes_falso.semanas = [semana_vacia]
    await service.eliminar_semana(2026, 10, 2)
    
    mes_falso.semanas = [semana_falsa]
    await service.eliminar_donacion_especifica(2026, 10, 1, "id-123")
    
    await service.vaciar_donaciones_semana(2026, 10, 1)
    
    semana_falsa.donaciones = [donacion_falsa]
    mes_falso.semanas = [semana_falsa]
    total = await service.contar_alimentos_mes_actual(2026, 10)
    assert total >= 5

@pytest.mark.asyncio
async def test_servicio_inicializar_mes_mockeado():
    repo = AsyncMock()
    repo.buscar_por_mes.return_value = None 
    service = DonacionService(repo)
    datos = InicializarMes(year=2026, mes=10)
    
    with patch("backend.donaciones.service.MesDonacion") as mock_mes:
        mock_mes.return_value = AsyncMock()
        await service.inicializar_nuevo_mes(datos)
        assert repo.insertar.called

@pytest.mark.asyncio
async def test_orquestador_eliminar_especifica_exito():
    don_service = AsyncMock()
    inv_service = AsyncMock()
    
    mes_falso = AsyncMock()
    semana_falsa = AsyncMock()
    semana_falsa.numero_semana = 1
    
    donacion_falsa = AsyncMock()
    donacion_falsa.id = "id-123"
    donacion_falsa.tipo_alimento = "Fideos"
    donacion_falsa.cantidad = 10
    donacion_falsa.fecha_vencimiento = date(2027, 1, 1)
    
    semana_falsa.donaciones = [donacion_falsa]
    mes_falso.semanas = [semana_falsa]
    don_service.obtener_mes_completo.return_value = mes_falso
    
    orq = EliminarDonacionOrquestador(don_service, inv_service)
    await orq.eliminar_especifica(2026, 10, 1, "id-123")
    assert inv_service.revertir_ingreso.called
    assert don_service.eliminar_donacion_especifica.called

def test_routers_donaciones():
    mock_service = AsyncMock()
    from backend.donaciones.schemas import ResumenTotalMes
    
    mock_service.obtener_total_mensual.return_value = ResumenTotalMes(year=2026, mes=10, total_alimentos_donados=10)
    mock_service.agregar_semana.return_value = {"mensaje": "OK"}
    mock_service.eliminar_semana.return_value = {"mensaje": "OK"}
    mock_service.modificar_fecha_creacion.return_value = {"mensaje": "OK"}
    
    app.dependency_overrides[get_donacion_service] = lambda: mock_service
    
    mock_orq_reg = AsyncMock()
    mock_orq_reg.ejecutar.return_value = {"mensaje": "OK"}
    app.dependency_overrides[get_registrar_donacion_orquestador] = lambda: mock_orq_reg
    
    mock_orq_del = AsyncMock()
    mock_orq_del.eliminar_especifica.return_value = {"mensaje": "OK"}
    mock_orq_del.vaciar_semana.return_value = {"mensaje": "OK"}
    app.dependency_overrides[get_eliminar_donacion_orquestador] = lambda: mock_orq_del
    
    assert client.put("/api/donaciones/2026/10", json={"numero_semana": 1, "tipo_alimento": "Arroz", "cantidad": 5, "fecha_vencimiento": "2027-01-01"}).status_code == 200
    assert client.get("/api/donaciones/2026/10/totales").status_code == 200
    assert client.post("/api/donaciones/2026/10/semanas").status_code == 200
    assert client.delete("/api/donaciones/2026/10/semana/1").status_code == 200
    assert client.patch("/api/donaciones/2026/10/fecha", json={"nueva_fecha": "01/01/2026"}).status_code == 200
    assert client.delete("/api/donaciones/2026/10/semanas/1/donaciones/id-123").status_code == 200
    assert client.delete("/api/donaciones/2026/10/semanas/1/donaciones").status_code == 200

@pytest.mark.asyncio
async def test_donaciones_repository_basicos():
    repo = DonacionRepository()
    doc_falso = AsyncMock()
    doc_falso.save = AsyncMock()
    doc_falso.insert = AsyncMock()
    
    await repo.guardar(doc_falso)
    assert doc_falso.save.called
    await repo.insertar(doc_falso)
    assert doc_falso.insert.called
