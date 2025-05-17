from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import create_async_engine, async_session, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

engine = create_async_engine("sqlite+aiosqlite:///app.db", echo=True) #echo - крутой параметр для дебага
new_session = async_sessionmaker(engine, expire_on_commit=False)

class DBModel(DeclarativeBase):
    pass

class AuthORM(DBModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str]


class TaskORM(DBModel):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(DBModel.metadata.create_all)

async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(DBModel.metadata.drop_all)