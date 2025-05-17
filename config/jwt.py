import datetime
from datetime import timedelta

from fastapi import HTTPException, Header
from jose import jwt, JWTError
from passlib.context import CryptContext

from config.config import setting

ctx = CryptContext(schemes=["bcrypt"])

def verify_password(password: str, hashed_password: str):
    return ctx.verify(password, hashed_password)

def get_hashed_password(password: str):
    return ctx.hash(password)

def create_token(data: dict):
    to_encode = data.copy()
    expire_time = datetime.datetime.now(datetime.UTC) + timedelta(minutes=setting.TOKEN_EXPIRE)
    to_encode["exp"] = expire_time
    tkn = jwt.encode(to_encode, setting.SECRET_KEY, setting.ALGORITHM)
    return tkn

def get_current_user(token: str = Header(..., alias="Authorization")) -> dict:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = token.replace("Bearer ", "")
        print("here1")
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        print("here2")
        user_id: str = payload.get("sub")
        print("\n\n", user_id, "\n\n")
        if user_id is None:
            raise credentials_exception
        return {"id": int(user_id)}
    except JWTError:
        raise credentials_exception