from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel): # а нужно ли при входе вводить ник?
    email: str
    password: str

class UserID(BaseModel):
    id: int

class LoginResponse(BaseModel):
    access_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    password: str
    class Config:
        from_attributes = True