import os
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt

    
def obtener_hash_password(password: str) -> str:

    pwd_bytes = password.encode('utf-8')

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    
    return hashed_password.decode('utf-8')

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    
    password_bytes = plain_password.encode('utf-8')

    hash_byte = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hash_byte)

def crear_token_jwt(data: dict) -> str:
    
    to_encode = data.copy()

    minutos_expiracion = int(os.getenv("JWT_EXPIRE_MINUTES", 120))

    expire = datetime.now(timezone.utc) + timedelta(minutes=minutos_expiracion)

    to_encode.update({"exp": expire})

    secret_key = os.getenv("JWT_SECRET_KEY")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    if not secret_key:
        raise ValueError("Falta JWT_SECRET_KEY en el archivo .env")

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt