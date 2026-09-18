import os
from dotenv import load_dotenv, find_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from backend.perfiles.models import Perfil
from backend.auth.models import Administrador
from backend.donaciones.models import MesDonacion
from backend.inventario.models import ItemInventario

load_dotenv(find_dotenv())


MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://localhost:27017"
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "iglesia_donaciones"
)


async def iniciar_base_de_datos():
    client = AsyncMongoClient(MONGO_URL)

    db = client[MONGO_DB]

    await init_beanie(
        database = db, 
        document_models = [Perfil, Administrador, MesDonacion, ItemInventario]
    )

    print("Base de datos MongoDB conectada y modelos registrados.")


   