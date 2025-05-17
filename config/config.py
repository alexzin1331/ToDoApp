from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "secret-key"
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRE: int = 20

setting = Settings()