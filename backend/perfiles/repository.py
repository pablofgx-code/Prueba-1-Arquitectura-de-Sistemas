from typing import List
from backend.perfiles.models import Perfil

class PerfilRepository:

    async def insertar(self, perfil: Perfil) -> Perfil:
        
        await perfil.insert()

        return perfil

    async def obtener_todos(self) -> List[Perfil]:

        return await Perfil.find_all().to_list()

    async def buscar_por_rut(self, rut: str) -> Perfil:

        return await Perfil.find_one(Perfil.rut == rut)

    async def guardar(self, perfil: Perfil) -> Perfil:

        await perfil.save()

        return perfil








