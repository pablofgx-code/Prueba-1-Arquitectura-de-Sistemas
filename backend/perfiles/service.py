import io
import openpyxl
from typing import List
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from backend.perfiles.models import Perfil
from backend.perfiles.schemas import PerfilCreate
from backend.perfiles.repository import PerfilRepository

class PerfilService:

    def __init__(self, repo: PerfilRepository):
        self.repo = repo
        
    async def crear_perfil(self, perfil_dto: PerfilCreate) -> Perfil:
        
        nuevo_perfil = Perfil(**perfil_dto.model_dump())
        
        return await self.repo.insertar(nuevo_perfil)

    async def obtener_por_rut(self, rut: str) -> Perfil:

        perfil = await self.repo.buscar_por_rut(rut)

        if not perfil:
            raise HTTPException(status_code=404, detail="Perfil no encontrado")

        return perfil

    async def obtener_todos(self) -> List[Perfil]:

        return await self.repo.obtener_todos()

    async def obtener_resumen_anual_retiros(self, year: int) -> List:

        perfiles = await self.repo.obtener_todos()
        
        resumen_list = []

        for perfil in perfiles:
            meses_retirados_este_year = [
                fecha.month for fecha in perfil.historial_retiros if fecha.year == year
            ]

            resumen_list.append({
                "rut" : perfil.rut,
                "nombre_completo" : f"{perfil.nombre} {perfil.apellido}",
                "meses_retirados" : meses_retirados_este_year 
            })

        return resumen_list

    async def registrar_retiro(self, rut: str) -> dict:
        
        perfil = await self.repo.buscar_por_rut(rut)
        if not perfil:
            raise HTTPException(status_code=404, detail="Perfil no encontrado.")

        fecha_actual = datetime.now().date()
        if fecha_actual in perfil.historial_retiros:
            raise HTTPException(status_code=400, detail="Esta persona ya tiene registrado un retiro el dia de hoy.")

        perfil.historial_retiros.append(fecha_actual)
        
        await self.repo.guardar(perfil)

        return {"mensaje" : f"Retiro registrado exitosamente para {perfil.nombre}"}

    async def generar_reporte_excel(self) -> StreamingResponse:

        perfiles = await self.repo.obtener_todos()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte de Retiros"

        meses_str = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        cabeceras = ["RUT", "Nombre", "Apellido"] + meses_str
        ws.append(cabeceras)
        
        anio_actual = datetime.now().year
        for perfil in perfiles:
            fila = [perfil.rut, perfil.nombre, perfil.apellido]
            meses_con_retiro = {fecha.month for fecha in perfil.historial_retiros if fecha.year == anio_actual}
            
            for mes_numero in range(1, 13):
                if mes_numero in meses_con_retiro:
                    fila.append("X")
                else:
                    fila.append("")
            ws.append(fila)
        
        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        
        return StreamingResponse(
            stream, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            headers={"Content-Disposition": f"attachment; filename=retiros_donaciones_{anio_actual}.xlsx"}
        )

    