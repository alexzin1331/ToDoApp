from fastapi import HTTPException, Depends

from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from starlette import status

from auth.models import UserModel, LoginResponse
from config.jwt import verify_password, create_token
from storage.repository import AuthRepo

router = APIRouter(prefix="/auth", tags=["tag2"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=dict)
async def register(user: UserModel):
    try:
        new_user = await AuthRepo.register_user(user)
        return {"id": new_user.id}
    except IntegrityError as e:
        if "username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )


@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserModel):
    try:
        user_db = await AuthRepo.get_user_by_username(user_data.username)
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User doesn't exists"
            )
        if not user_db or not verify_password(user_data.password, user_db.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        token_data = {
            "sub": str(user_db.id),
            "email": user_db.email,
            "username": user_db.username
        }
        print("\n\n",token_data, "\n\n")
        token = create_token(token_data)
        return LoginResponse(access_token=token)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error: " + str(e)
        )