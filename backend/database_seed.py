

import logging
from datetime import date, datetime

from backend.auth.models import Administrador
from backend.perfiles.models import Perfil
from backend.donaciones.models import MesDonacion
from backend.inventario.models import (
    LotePerecible,
    RegistroSalida,
    ItemLlevado,
)


logger = logging.getLogger("uvicorn")


async def poblar_base_de_datos():
    """Inserta datos de prueba si la base de datos está vacía."""

    # ============================================================
    # 1. Seed de Administradores
    # ============================================================

    if await Administrador.count() == 0:
        admin = Administrador(
            nombre="Admin Iglesia",
            email="admin@iglesia.org",
            hashed_password=(
                "$2b$12$jV0gSp2f733fSpDtiX9bRuutJXYHD1SDMAjbcVH.0MzWehXh1bOjC"
            ),
            activo=True,
        )

        await admin.insert()

        logger.info(
            "🟢 Seed: Administrador inicial creado "
            "(admin@iglesia.org)."
        )

    # ============================================================
    # 2. Seed de Perfiles
    # ============================================================

    if await Perfil.count() == 0:
        perfiles = [
            Perfil(
                nombre="Juan",
                apellido="Pérez",
                rut="12.345.678-9",
                contacto="+56912345678",
                fecha_nacimiento=date(1985, 5, 15),
                edad=41,
                situacion_calle=False,
                activo=True,
            ),
            Perfil(
                nombre="Ana",
                apellido="González",
                rut="20.111.222-3",
                contacto="+56987654321",
                fecha_nacimiento=date(1990, 8, 22),
                edad=36,
                situacion_calle=True,
                motivo_situacion="Desempleo",
                activo=True,
            ),
        ]
        await Perfil.insert_many(perfiles)
        logger.info("🟢 Seed: Perfiles iniciales creados.")

    # ============================================================
    # 3. Donaciones
    # ============================================================
    if await MesDonacion.count() == 0:
        mes_octubre = MesDonacion(
            year=2026,
            mes=10,
            fecha_creacion="01/10/2026",
            semanas=[
                {
                    "numero_semana": 1,
                    "donaciones": [
                        {"id": "don-001", "tipo_alimento": "Arroz", "cantidad": 25, "fecha_vencimiento": date(2027, 6, 30)},
                        {"id": "don-002", "tipo_alimento": "Fideos", "cantidad": 40, "fecha_vencimiento": date(2027, 8, 15)},
                    ],
                },
                {
                    "numero_semana": 2,
                    "donaciones": [
                        {"id": "don-003", "tipo_alimento": "Leche Entera", "cantidad": 15, "fecha_vencimiento": date(2026, 12, 1)},
                        {"id": "don-004", "tipo_alimento": "Aceite", "cantidad": 10, "fecha_vencimiento": date(2028, 1, 1)},
                    ],
                },
            ],
        )
        await mes_octubre.insert()
        logger.info("🟢 Seed: Donaciones de prueba creadas.")

    # ============================================================
    # 4. Inventario
    # ============================================================
    if await LotePerecible.count() == 0:
        lotes = [
            LotePerecible(tipo_alimento="Arroz", cantidad_disponible=25, fecha_vencimiento=date(2027, 6, 30)),
            LotePerecible(tipo_alimento="Leche Entera", cantidad_disponible=15, fecha_vencimiento=date(2026, 12, 1)),
            LotePerecible(tipo_alimento="Aceite", cantidad_disponible=10, fecha_vencimiento=date(2028, 1, 1)),
        ]
        await LotePerecible.insert_many(lotes)
        logger.info("🟢 Seed: Lotes de inventario creados.")

    # ============================================================
    # 5. Registro de Salidas
    # ============================================================
    if await RegistroSalida.count() == 0:
        salidas = [
            RegistroSalida(
                fecha=datetime.now(),
                rut_beneficiario="12.345.678-9",
                alimentos_entregados=[ItemLlevado(tipo_alimento="Fideos", cantidad=10)],
            ),
            RegistroSalida(
                fecha=datetime.now(),
                rut_beneficiario="20.111.222-3",
                alimentos_entregados=[ItemLlevado(tipo_alimento="Arroz", cantidad=5)],
            ),
        ]
        await RegistroSalida.insert_many(salidas)
        logger.info("🟢 Seed: Historial de salidas creado.")