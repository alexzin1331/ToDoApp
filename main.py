from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from auth import AuthHandlers
from storage.storage import create_tables, drop_tables
from tasks import TaskHandlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await drop_tables()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(TaskHandlers.router)
app.include_router(AuthHandlers.router)

@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")