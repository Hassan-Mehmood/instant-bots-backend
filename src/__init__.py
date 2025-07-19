from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.routers.chat_router import chat_router
from src.routers.user_router import user_router
from src.routers.bot_router import bot_router
from src.routers.router import router as api_router
from src.webhooks.clerk_webhooks import router as clerk_webhook_router
from src.routers.payment_router import router as payment_router
from src.db.database import get_db
from src.models.models import Bot, User
from sqlalchemy.orm import Session


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",  # /api/v1/openapi.json
    docs_url="/docs",  # /api/v1/docs
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
app.include_router(user_router)
app.include_router(bot_router)
app.include_router(clerk_webhook_router)
app.include_router(api_router)
app.include_router(payment_router)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/aggregate/{user_id}")
async def aggregate(user_id: str, db: Session = Depends(get_db)):
    bots = db.query(Bot).count()
    user = db.query(User).filter(User.clerk_id == user_id).first()

    if not user:
        return {"error": "User not found"}

    total_credits = user.credits

    return {
        "bots": bots,
        "total_credits": total_credits,
    }
