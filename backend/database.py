from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.perfiles.models import Perfil

async def iniciar_base_de_datos():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    
    db = client.iglesia_donaciones

    await init_beanie(database=db, document_models=[Perfil])
    
    print("Base de datos MongoDB conectada y modelos registrados.")