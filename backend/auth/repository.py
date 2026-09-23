from beanie import PydanticObjectId
from backend.auth.models import Administrador

class AdministradorRepository:

    async def buscar_por_email(self, email: str) -> Administrador | None:

        return await Administrador.find_one(Administrador.email == email)

    async def buscar_por_id(self, admin_id: str) -> Administrador | None:

        return await Administrador.get(PydanticObjectId(admin_id))

    async def crear(self, admin: Administrador) -> Administrador:
        
        await admin.insert()
        
        return admin

    async def actualizar(self, admin: Administrador) -> Administrador:

        await admin.save()

        return admin



    