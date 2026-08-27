from beanie import Document

class Administrador(Document):

    email: str
    nombre: str
    hashed_password: str
    activo: bool = True

    class Settings:
        name = "administradores"


    