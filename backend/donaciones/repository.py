from backend.donaciones.models import MesDonacion

class DonacionRepository:

    async def buscar_por_mes(self, year: int, mes: int) -> MesDonacion | None:
        return await MesDonacion.find_one(
            MesDonacion.year == year,
            MesDonacion.mes == mes
        )

    async def guardar(self, documento: MesDonacion) -> MesDonacion:
        await documento.save()
        return documento

    async def insertar(self, documento: MesDonacion) -> MesDonacion:
        await documento.insert()
        return documento




