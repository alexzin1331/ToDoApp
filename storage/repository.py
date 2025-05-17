
from fastapi import HTTPException

from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from auth.models import UserModel, UserID, UserResponse
from config.config import setting
from config.jwt import get_hashed_password
from storage.storage import new_session, TaskORM, AuthORM
from pydantic import ConfigDict
from sqlalchemy import select

from tasks.models import TaskModel, TaskID, AddRequest, EditRequest

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class TaskModelDB(TaskModel):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AuthRepo:
    @classmethod
    async def register_user(cls, u: UserModel) -> UserID:
        async with new_session() as session:
            existing_user = await session.execute(
                select(AuthORM).where((AuthORM.username == u.username) | (AuthORM.email == u.email)))
            if existing_user.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail="Username or email already exists"
                )

            new_user = AuthORM(
                username=u.username,
                email=u.email,
                password=get_hashed_password(u.password)
            )

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return UserID(id=new_user.id)
    @classmethod
    async def get_user_by_id(cls, token: str = Depends(oauth2_scheme)) -> UserModel:
        cred_exception = HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            tkn = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
            user_id = tkn.get("sub")
            if user_id is None:
                raise cred_exception
        except JWTError:
            raise cred_exception

        async with new_session() as session:
            query = select(AuthORM).where(AuthORM.id == user_id)
            user_db = await session.execute(query)
            user_prepare = user_db.scalars().first()
            user = UserModel.model_validate(user_prepare)
        return user
    @classmethod
    async def get_user_by_username(cls, username: str) -> UserResponse | None:
        async with new_session() as session:
            query = select(AuthORM).where(AuthORM.username == username)
            result = await session.execute(query)
            user_orm = result.scalars().first()
            if user_orm is None:
                return None
            res = UserResponse.model_validate(user_orm)
            print("\n", res, "\n")
            return res

class TaskRepo:
    @classmethod
    async def add_task_DB(cls, t: AddRequest, user_id: int) -> TaskID:
        async with new_session() as session:
            data = t.model_dump()
            new_task = TaskORM(**data, user_id=user_id) # create record in python (no db)
            session.add(new_task)
            await session.commit()
        return TaskID(id=new_task.id)

    @classmethod
    async def get_tasks_DB(cls, user_id: int) -> list[TaskModelDB]:
        async with new_session() as session:
            query = select(TaskORM).where(TaskORM.user_id == user_id)
            tasks_db = await session.execute(query)
            tasks_arr = tasks_db.scalars().all()
            tasks = [TaskModelDB.model_validate(t) for t in tasks_arr]
            print("tasks getting")
        return tasks

    @classmethod
    async def delete_task_DB(cls, task_id: int, user_id: int) -> TaskID:
        async with new_session() as session:
            res = await session.execute(
                select(TaskORM).where(TaskORM.user_id == user_id).where(TaskORM.id == task_id)
            )
            await session.delete(res.scalars().first())
            await session.commit()
        return TaskID(id=task_id)

    @classmethod
    async def edit_task_DB(cls, edit: EditRequest, user_id: int) -> TaskID:
        async with new_session() as session:
            res = await session.execute(
                select(TaskORM).where(TaskORM.user_id == user_id).where(TaskORM.id == edit.id)
            )
            edit_task = res.scalars().first()
            if edit.name is not None:
                edit_task.name = edit.name
            if edit.description is not None:
                edit_task.description = edit.description
            session.add(edit_task)
            await session.commit()
        return TaskID(id=edit.id)
