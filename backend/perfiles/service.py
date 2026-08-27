from typing import List
from backend.perfiles.models import Perfil
from backend.perfiles.schemas import PerfilCreate

class PerfilService:

    async def crear_perfil(self, perfil_dto: PerfilCreate) -> Perfil:
        
        nuevo_perfil = Perfil(**perfil_dto.model_dump())
        
        await nuevo_perfil.insert()
        
        return nuevo_perfil

    async def obtener_todos(self) -> List[Perfil]:

        return await Perfil.find_all().to_list()


    