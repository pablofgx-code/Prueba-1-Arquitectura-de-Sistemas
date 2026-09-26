

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
                "$2b$12$eImiTXuWVxfM37uY4JANjOL."
                "8844ZXE.tQ3B0k6eT1p3S6z/bCkW"
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
        perfil = Perfil(
            nombre="Juan",
            apellido="Pérez",
            rut="12.345.678-9",
            contacto="+56912345678",
            fecha_nacimiento=date(1985, 5, 15),
            edad=41,
            situacion_calle=False,
            motivo_situacion=None,
            historial_retiros=[],
            activo=True,
        )

        await perfil.insert()

        logger.info("🟢 Seed: Perfil inicial creado.")

    # ============================================================
    # 3. Seed de Donaciones
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
                        {
                            "id": "don-001",
                            "tipo_alimento": "Arroz",
                            "cantidad": 25,
                            "fecha_vencimiento": date(2027, 6, 30),
                        },
                        {
                            "id": "don-002",
                            "tipo_alimento": "Fideos",
                            "cantidad": 40,
                            "fecha_vencimiento": date(2027, 8, 15),
                        },
                    ],
                },
                {
                    "numero_semana": 2,
                    "donaciones": [
                        {
                            "id": "don-003",
                            "tipo_alimento": "Leche Entera",
                            "cantidad": 15,
                            "fecha_vencimiento": date(2026, 12, 1),
                        },
                    ],
                },
            ],
        )

        await mes_octubre.insert()

        logger.info(
            "🟢 Seed: Registros de donaciones de prueba creados."
        )

    # ============================================================
    # 4. Seed de Inventario
    # ============================================================

    if await LotePerecible.count() == 0:
        lote1 = LotePerecible(
            tipo_alimento="Arroz",
            cantidad_disponible=25,
            fecha_vencimiento=date(2027, 6, 30),
        )

        lote2 = LotePerecible(
            tipo_alimento="Leche Entera",
            cantidad_disponible=15,
            fecha_vencimiento=date(2026, 12, 1),
        )

        await LotePerecible.insert_many([
            lote1,
            lote2,
        ])

        logger.info("🟢 Seed: Lotes de inventario creados.")

    # ============================================================
    # 5. Seed de Registro de Salidas
    # ============================================================

    if await RegistroSalida.count() == 0:
        salida = RegistroSalida(
            fecha=datetime.now(),
            rut_beneficiario="12.345.678-9",
            alimentos_entregados=[
                ItemLlevado(
                    tipo_alimento="Fideos",
                    cantidad=10,
                )
            ],
        )

        await salida.insert()

        logger.info("🟢 Seed: Historial de salidas creado.")

