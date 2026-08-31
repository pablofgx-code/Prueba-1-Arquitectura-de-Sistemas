from fastapi import HTTPException, status
from backend.auth.models import Administrador 
from backend.auth.schemas import AdministradorCreate, LoginData
from backend.auth import security

class AuthService:

    async def registrar_admin(self, admin_dto: AdministradorCreate) -> Administrador:
        
        admin_existente = await Administrador.find_one(Administrador.email == admin_dto.email)
        
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

        await nuevo_admin.insert()

        return nuevo_admin

    async def autenticar_admin(self, login_dto: LoginData) -> Administrador:

        admin = await Administrador.find_one(Administrador.email == login_dto.email)

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

