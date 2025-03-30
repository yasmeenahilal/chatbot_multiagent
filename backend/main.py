from contextlib import asynccontextmanager

from database.base import init_db
from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from router.user import router as user_router
from fastapi.middleware.cors import CORSMiddleware



@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"server is starting ... ")
    await init_db()
    yield
    print(f"server is stopping ... ")


app = FastAPI(
    title="chatbot",
    description="A REST API for chatbot and auth",
    version="v1",
    lifespan=life_span,
)

# CORS Configuration
origins = [
    "http://localhost:3000",  # Allow your frontend's origin (Next.js dev server)
    "https://yourfrontenddomain.com",  # Replace with your production frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins in the list
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Allow methods (POST for login)
    allow_headers=["*"],  # Allow all headers (can be restrictive if needed)
)

@app.get("/")
async def index():
    return {"welcome": "how are you doing"}


app.include_router(user_router, prefix="/user", tags=["users"])
