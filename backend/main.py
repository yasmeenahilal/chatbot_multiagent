from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from database.base import init_db
from router.user import router as user_router

@asynccontextmanager
async def life_span(app:FastAPI):
    print(f"server is starting ... ")
    await init_db()
    yield
    print(f"server is stopping ... ")

app = FastAPI(
    title="chatbot",
    description="A REST API for chatbot and auth",
    version="v1",
    lifespan=life_span
)

@app.get('/')
async def index():
    return {
        "welcome":"how are you doing"
    }

app.include_router(user_router, prefix='/user', tags=['users'])