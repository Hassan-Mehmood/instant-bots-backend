from fastapi import APIRouter
from src.models.models import Chat
from src.db.database import SessionLocal

from sqlalchemy.orm import joinedload
from sqlalchemy import select

user_router = APIRouter(prefix='/user')

database = SessionLocal()
@user_router.get("/{user_id}/chats")
async def get_chats(user_id: str):
    result = database.execute(select(Chat)
    .options(joinedload(Chat.messages))
    .options(joinedload(Chat.bot))
    .filter_by(user_id=user_id)).unique().scalars().all() 

    return result