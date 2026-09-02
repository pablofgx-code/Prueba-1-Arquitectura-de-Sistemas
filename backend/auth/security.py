import os
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not SECRET_KEY:
    raise ValueError("Falta JWT_SECRET_KEY en el archivo")
    
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

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def crear_token_recuperacion(email: str) -> str:

    minutos_expiracion = 15
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutos_expiracion)

    to_encode = {
        "sub": email,
        "scope": "recuperacion",
        "exp": expire
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decodificar_token_recuperacion(token: str) -> str | None:

    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) 

        if payload.get("scope") != "recuperacion":
            return None

        return payload.get("sub")

    except JWTError:
        return None


