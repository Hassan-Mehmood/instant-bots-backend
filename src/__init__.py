from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.routers.chat_router import chat_router

from src.models.models import SessionLocal, User, Bot
from src.constants.prompts_dict import PROMPTS
from uuid import uuid4

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1}/openapi.json", # /api/v1/openapi.json
    docs_url=f"{settings.API_V1}/docs", # /api/v1/docs
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"stauts": "ok"}

@app.post("/user/create")
async def create_user():
    sessoin = SessionLocal()

    user = User(
        id = str(uuid4()),
        username = "Hassan",
        email = "hassan@hassan.com",
        password = "123456",
        credits = 0,
    )

    sessoin.add(user)
    sessoin.commit()

@app.post('/bot/create')
async def create_bot():
    session = SessionLocal()

    bot = Bot(
        id = str(uuid4()),
        name = "RESUME_WRITER",
        description = "This bot will write a resume for you.",
        prompt = PROMPTS['RESUME_WRITER'],
        price = 0,
        transactions = [],
        chats = [],
    )

    session.add(bot)
    session.commit()