from fastapi import HTTPException, status
from backend.auth.models import Administrador 
from backend.auth.schemas import AdministradorCreate, LoginData, CambiarPassword, SolicitudRecuperacion, RestablecerPassword
from backend.auth import security
from backend.auth.repository import AdministradorRepository

class AuthService:

    def __init__(self, repo: AdministradorRepository):

        self.repo = repo

    async def registrar_admin(self, admin_dto: AdministradorCreate) -> Administrador:
        
        admin_existente = await self.repo.buscar_por_email(admin_dto.email)
        
        if admin_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo ya esta registrado en el sistema."
            )

        password_encriptada = security.obtener_hash_password(admin_dto.password)

        nuevo_admin = Administrador(
            email=admin_dto.email,
            nombre=admin_dto.nombre,
            hashed_password=password_encriptada    
        )

        return await self.repo.crear(nuevo_admin)

    async def autenticar_admin(self, login_dto: LoginData) -> Administrador:

        admin = await self.repo.buscar_por_email(login_dto.email)

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos."
            )

        if not security.verificar_password(login_dto.password, admin.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos."
            )

        if not admin.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta cuenta ha sido desactivada."
            )

        return admin

    def generar_token_para_admin(self, admin: Administrador) -> str:

        token_data = {"sub": str(admin.id), "email": admin.email}

        return security.crear_token_jwt(token_data)

    async def cambiar_password(self, admin: Administrador, datos: CambiarPassword) -> dict:

        if not security.verificar_password(datos.password_actual, admin.hashed_password):
            raise HTTPException(status_code=401, detail="La contraseña actual es incorrecta")

        if security.verificar_password(datos.nueva_password, admin.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="La nueva contraseña no puede ser igual a la anterior"
            )

        admin.hashed_password = security.obtener_hash_password(datos.nueva_password)

        await self.repo.actualizar(admin)

        return {"mensaje": "La contraseña ha sido actualizada de manera exitosa :D"}

    async def solicitar_recuperacion(self, datos: SolicitudRecuperacion) -> dict:

        admin = await self.repo.buscar_por_email(datos.email)

        respuesta_estandar = {
            "mensaje" : "Si el correo esta registrado en el sistema, recibiras las instrucciones en breves"
        }

        if not admin or not admin.activo:
            return respuesta_estandar

        token_recuperacion = security.crear_token_recuperacion(admin.email)

        print("\n" + "=" * 60)
        print("📨 [SIMULADOR EMAIL] Notificación de Restablecimiento de Clave")
        print(f"Destinatario : {admin.email}")
        print("Token generado (Válido por 15 minutos):")
        print(token_recuperacion)
        print("=" * 60 + "\n")

        return respuesta_estandar

    async def restablecer_password(self, datos: RestablecerPassword) -> dict:

        email = security.decodificar_token_recuperacion(datos.token)

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token de recuperacion es invalido o ha caducado."
            )

        admin = await self.repo.buscar_por_email(email)
        if not admin or not admin.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o inactivo."
            )
        
        if security.verificar_password(datos.nueva_password, admin.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña no puede ser igual a la anterior."
            )

        admin.hashed_password = security.obtener_hash_password(datos.nueva_password)
        
        await self.repo.actualizar(admin)

        return {"mensaje" : "La contraseña se restablecio exitosamente. Ahora puedes iniciar sesion con tu nueva contraseña."}

