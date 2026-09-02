from fastapi import APIRouter, Depends, status, Response
from backend.auth.schemas import (
    AdministradorCreate, AdministradorResponse, LoginData, CambiarPassword,
    SolicitudRecuperacion, RestablecerPassword
    )
from backend.auth.service import AuthService
from backend.auth.models import Administrador
from backend.auth.dependencies import obtener_admin_actual

router = APIRouter(prefix="/api/auth", tags=["Autenticacion"])

def get_auth_service() -> AuthService:

    return AuthService()

@router.post("/registro", response_model=AdministradorResponse, status_code=status.HTTP_201_CREATED)
async def registrar_administrador(
    admin: AdministradorCreate,
    service: AuthService = Depends(get_auth_service)
):
    return await service.registrar_admin(admin)

@router.post("/login")
async def iniciar_sesion(
    credenciales: LoginData,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):

    admin = await service.autenticar_admin(credenciales)

    token = service.generar_token_para_admin(admin)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7200
    )

    return {
            "mensaje": "Inicio de sesion exitoso", 
            "admin": admin.nombre
           }

@router.put("/cambiar-password")
async def modificar_password(
    datos: CambiarPassword,
    admin_actual: Administrador = Depends(obtener_admin_actual),
    service: AuthService = Depends(get_auth_service)
):
    return await service.cambiar_password(admin_actual, datos)

@router.post("/solicitar-recuperacion")
async def solicitar_recuperacion_password(
    datos: SolicitudRecuperacion,
    service: AuthService = Depends(get_auth_service)
):
    return await service.solicitar_recuperacion(datos)

@router.post("/restablecer-password")
async def restablecer_password(
    datos: RestablecerPassword,
    service: AuthService = Depends(get_auth_service)
):
 
    return await service.restablecer_password(datos)

@router.post("/logout")
async def cerrar_sesion(
    response: Response,
    admin_actual: Administrador = Depends(obtener_admin_actual)
):

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"mensaje" : f"Sesion cerrada de manera exitosa, hasta la proxima, {admin_actual.nombre}"}




