from datetime import datetime
from fastapi import HTTPException, status
from backend.donaciones.models import MesDonacion, Semana, DonacionAlimento
from backend.donaciones.schemas import InicializarMes, AgregarDonaciones, ResumenTotalMes
from backend.donaciones.repository import DonacionRepository

class DonacionService:
    
    def __init__(self, repo: DonacionRepository):
        self.repo = repo

    async def inicializar_nuevo_mes(self, datos: InicializarMes) -> MesDonacion:
        
        existe = await self.repo.buscar_por_mes(datos.year, datos.mes)
        if existe:
            raise HTTPException(status_code=400, detail="Este mes ya esta inicializado")

        semanas_iniciales = [Semana(numero_semana=i, donaciones=[]) for i in range(1, 5)]

        fecha_actual = datetime.now().strftime("%d/%m/%y")

        nuevo_mes = MesDonacion(
            year = datos.year,
            mes = datos.mes,
            fecha_creacion=fecha_actual,
            semanas = semanas_iniciales
        )

        return await self.repo.insertar(nuevo_mes)

    async def registra_donacion(self, year: int, mes: int, datos: AgregarDonaciones) -> dict:
        
        mes_doc = await self._obtener_mes_o_fallar(year, mes)
        
        semana_destino: Semana = self._obtener_semana_o_fallar(mes_doc, datos.numero_semana)

        nueva_donacion= DonacionAlimento(
            tipo_alimento = datos.tipo_alimento,
            cantidad = datos.cantidad
        )

        semana_destino.donaciones.append(nueva_donacion)

        await self.repo.guardar(mes_doc)
        
        return {"mensaje" : "Donacion registrado exitosamente."}

    async def obtener_mes_completo(self, year: int, mes: int) -> MesDonacion:

        mes_doc = await self._obtener_mes_o_fallar(year, mes)

        return mes_doc

    async def obtener_total_mensual(self, year: int, mes: int) -> ResumenTotalMes:

        mes_doc = await self._obtener_mes_o_fallar(year, mes)

        total = sum(donacion.cantidad for semana in mes_doc.semanas for donacion in semana.donaciones)

        return ResumenTotalMes(
            year = mes_doc.year,
            mes = mes_doc.mes,
            total_alimentos_donados = total
        )

    async def modificar_fecha_creacion(self, year: int, mes: int, nueva_fecha: str) -> dict:
        
        mes_doc = await self._obtener_mes_o_fallar(year, mes)

        mes_doc.fecha_creacion = nueva_fecha

        await self.repo.guardar(mes_doc)

        return {"mensaje" : f"Fecha de creacion actualizada a {nueva_fecha}"}

    async def agregar_semana(self, year: int, mes: int) -> dict:

        mes_doc = await self._obtener_mes_o_fallar(year, mes)

        if len(mes_doc.semanas) >= 5:
            raise HTTPException(status_code=400, detail="El mes ya tiene el limite maximo de 5 semanas.")

        semanas_existentes = {s.numero_semana for s in mes_doc.semanas}

        siguiente_numero = next(i for i in range(1, 6) if i not in semanas_existentes)

        nueva_semana = Semana(numero_semana = siguiente_numero, donaciones = [])
        
        mes_doc.semanas.append(nueva_semana)

        mes_doc.semanas.sort(key=lambda s: s.numero_semana)

        await self.repo.guardar(mes_doc)

        return {"mensaje" : f"La semana {siguiente_numero} se agrego de manera exitosa."}

    async def eliminar_semana(self, year: int, mes: int, numero_semana: int) -> dict:

        mes_doc = await self._obtener_mes_o_fallar(year, mes)

        semana_a_eliminar: Semana = self._obtener_semana_o_fallar(mes_doc, numero_semana)

        if len(semana_a_eliminar.donaciones) > 0:
            raise HTTPException(
                status_code=400,
                detail="No puede eliminar esta semana porque tiene donaciones registradas. Elimine las donaciones primero."
            )

        mes_doc.semanas = [s for s in mes_doc.semanas if s.numero_semana != numero_semana]

        await self.repo.guardar(mes_doc)

        return {"mensaje" : f"Semana {numero_semana} eliminada exitosamente."}

    async def eliminar_donacion_especifica(self, year: int, mes: int, numero_semana: int, donacion_id: str) -> dict:

        mes_doc = await self._obtener_mes_o_fallar(year, mes)

        semana_destino: Semana = self._obtener_semana_o_fallar(mes_doc, numero_semana)

        donacion_existe = any(d.id == donacion_id for d in semana_destino.donaciones)
        if not donacion_existe:
            raise HTTPException(status_code=404, detail="La donacion especifica no existe")

        semana_destino.donaciones = [d for d in semana_destino.donaciones if d.id != donacion_id]

        await self.repo.guardar(mes_doc)
        return {"mensaje" : "Donacion eliminada exitosamente"}

    async def vaciar_donaciones_semana(self, year: int, mes: int, numero_semana: int) -> dict:
        
        mes_doc = await self._obtener_mes_o_fallar(year, mes)
        
        semana_destino: Semana = self._obtener_semana_o_fallar(mes_doc, numero_semana)

        semana_destino.donaciones = []

        await self.repo.guardar(mes_doc)

        return {"mensaje" : f"Se han eliminado todas las donaciones de la semana {numero_semana}"}


    def _obtener_semana_o_fallar(self, mes_doc: MesDonacion, numero_semana: int) -> Semana:

        semana_destino = next((s for s in mes_doc.semanas if s.numero_semana == numero_semana), None)

        if not semana_destino:
            raise HTTPException(status_code=404, detail="Semana no encontrada")
        
        return semana_destino
    
    async def _obtener_mes_o_fallar(self, year: int, mes: int) -> MesDonacion:

        mes_doc = await self.repo.buscar_por_mes(year, mes)

        if not mes_doc:
            raise HTTPException(status_code=404, detail="Mes no encontrado.")
        
        return mes_doc


