from fastapi import APIRouter, HTTPException
from src.models.models import Chat, User
from src.db.database import SessionLocal

from sqlalchemy.orm import joinedload
from sqlalchemy import select

from src.routers.utils import check_uuid

user_router = APIRouter(prefix='/user')

database = SessionLocal()
@user_router.get("/{user_id}/chats")
async def get_chats(user_id: str):
    result = database.execute(select(Chat)
    .options(joinedload(Chat.messages))
    .options(joinedload(Chat.bot))
    .filter_by(user_id=user_id)).unique().scalars().all() 

    return result


@user_router.get("/credits/{user_id}")
async def user_credits(user_id):
    try:
        if not user_id or not check_uuid(user_id):
            raise HTTPException(status_code=400, detail="Please provide a valid user id")
        
        user = database.query(User).filter_by(id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "credits": user.credits,
            "status": 200,
        }

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in user_credits: ", str(e))
        return {
            "status": 500,
            "credits": None
        }