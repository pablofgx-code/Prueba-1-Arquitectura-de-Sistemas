import os
from dotenv import load_dotenv, find_dotenv
from pymongo import AsyncMongoClient
from beanie import init_beanie

from backend.perfiles.models import Perfil
from backend.auth.models import Administrador
from backend.donaciones.models import MesDonacion
from backend.inventario.models import LotePerecible, RegistroSalida


load_dotenv(find_dotenv())


async def iniciar_base_de_datos():

    mongo_url = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017"
    )

    nombre_base_datos = os.getenv(
        "DATABASE_NAME",
        "iglesia_donaciones"
    )

    if not mongo_url or not nombre_base_datos:
        raise ValueError(
            "Faltan variables de entorno para la Base de Datos"
        )

    client = AsyncMongoClient(mongo_url)
    db = client[nombre_base_datos]

    await init_beanie(
        database=db,
        document_models=[
            Perfil,
            Administrador,
            MesDonacion,
            LotePerecible,
            RegistroSalida
        ]
    )

    print(
        f"Base de datos MongoDB conectada. "
        f"{mongo_url} / {nombre_base_datos}"
    )