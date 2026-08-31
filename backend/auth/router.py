from fastapi import APIRouter, Depends, status, Response
from backend.auth.schemas import AdministradorCreate, AdministradorResponse, LoginData
from backend.auth.service import AuthService

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




