import os

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from backend.perfiles.models import Perfil


MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://localhost:27017"
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "iglesia_donaciones"
)


async def iniciar_base_de_datos():
    client = AsyncIOMotorClient(MONGO_URL)

    db = client[MONGO_DB]

    await init_beanie(
        database=db,
        document_models=[Perfil]
    )

    print("Base de datos MongoDB conectada y modelos registrados.")