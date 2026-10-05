import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app
from backend.database import iniciar_base_de_datos
from backend.database_seed import poblar_base_de_datos

client = TestClient(app)

def test_pagina_principal():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@pytest.mark.asyncio
@patch("backend.database.init_beanie")
@patch("backend.database.AsyncMongoClient")
async def test_iniciar_base_de_datos_exito(mock_motor, mock_init_beanie):
    with patch.dict(os.environ, {"MONGODB_URL": "mongodb://localhost", "DATABASE_NAME": "test_db"}):
        await iniciar_base_de_datos()
        assert mock_motor.called
        assert mock_init_beanie.called

@pytest.mark.asyncio
async def test_iniciar_base_de_datos_error():
    with patch("backend.database.os.getenv", return_value=""):
        with pytest.raises(ValueError) as exc:
            await iniciar_base_de_datos()
        assert "Faltan variables" in str(exc.value)

@pytest.mark.asyncio
@patch("backend.database_seed.RegistroSalida")
@patch("backend.database_seed.LotePerecible")
@patch("backend.database_seed.MesDonacion")
@patch("backend.database_seed.Perfil")
@patch("backend.database_seed.Administrador")
async def test_poblar_base_de_datos(mock_admin, mock_perfil, mock_mes, mock_lote, mock_salida):
    for m in (mock_admin, mock_perfil, mock_mes, mock_lote, mock_salida):
        m.count = AsyncMock(return_value=1)
    await poblar_base_de_datos()
    assert mock_admin.count.called