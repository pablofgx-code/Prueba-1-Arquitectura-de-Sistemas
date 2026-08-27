import os
from dotenv import load_dotenv, find_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.perfiles.models import Perfil

load_dotenv(find_dotenv())

async def iniciar_base_de_datos():

    url_base_datos = os.getenv("MONGODB_URL")
    nombre_base_datos = os.getenv("DATABASE_NAME")
    
    if not url_base_datos or not nombre_base_datos:
        raise ValueError("Faltan variables de entorno para la Base de Datos")
    
    client = AsyncIOMotorClient(url_base_datos)
    
    db = client[nombre_base_datos]

    await init_beanie(database=db, document_models=[Perfil])
    
    print(f"Base de datos MongoDB conectada. {nombre_base_datos}")