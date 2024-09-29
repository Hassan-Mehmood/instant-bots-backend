from fastapi import APIRouter
from src.models.models import Bot
from src.db.database import SessionLocal

from sqlalchemy.orm import joinedload
from sqlalchemy import select

bot_router = APIRouter(prefix='/bot')

database = SessionLocal()
@bot_router.get("/all-bots")
async def get_chats():
    result = database.query(Bot).all()

    return result