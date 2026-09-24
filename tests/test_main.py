import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from backend.database import iniciar_base_de_datos


client = TestClient(app)

def test_pagina_principal():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@pytest.mark.asyncio
@patch("backend.database.init_beanie")
@patch("backend.database.AsyncMotorClient")
async def test_iniciar_base_de_datos_exito(mock_motor, mock_init_beanie):
    with patch.dict(os.environ, {"MONGO_URL": "mongodb://localhost", "DATABASE_NAME": "test_db"}):
        await iniciar_base_de_datos()
        assert mock_motor.called
        assert mock_init_beanie.called

@pytest.mark.asyncio
async def test_iniciar_base_de_datos_error():
    with patch("backend.database.os.getenv", return_value=""):
        with pytest.raises(ValueError) as exc:
            await iniciar_base_de_datos()
        assert "Faltan variables" in str(exc.value)