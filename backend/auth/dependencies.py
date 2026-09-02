import os 
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from beanie import PydanticObjectId
from backend.auth.models import Administrador
from backend.auth.security import SECRET_KEY, ALGORITHM

async def obtener_admin_actual(request: Request) ->Administrador:

    token_con_prefijo = request.cookies.get("access_token")

    if not token_con_prefijo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado. Por favor, inicia sesion."
        )

    token = token_con_prefijo.replace("Bearer ", "")

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        admin_id = payload.get("sub")
        if admin_id is None:
            raise HTTPException(status_code=401, detail="Token corrupto.")

    except JWTError:

        raise HTTPException(status_code=401, detail="La sesion ha expirado o es invalida")

    admin = await Administrador.get(PydanticObjectId(admin_id))

    if not admin or not admin.activo:
        raise HTTPException(status_code=401, detail="Administrador no encontrado o inactivo")

    return admin
    