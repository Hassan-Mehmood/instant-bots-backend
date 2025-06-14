from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.models.models import Chat, User
from src.db.database import SessionLocal

from sqlalchemy.orm import joinedload
from sqlalchemy import select

from src.routers.utils import check_uuid

user_router = APIRouter(prefix="/users", tags=["users"])

database = SessionLocal()


@user_router.get("/{user_id}/chats")
async def get_chats(user_id: str):
    if not user_id or not check_uuid(user_id):
        raise HTTPException(status_code=400, detail="Please provide a valid user id")

    result = (
        database.execute(
            select(Chat)
            .options(joinedload(Chat.messages))
            .options(joinedload(Chat.bot))
            .filter_by(user_id=user_id)
        )
        .unique()
        .scalars()
        .all()
    )

    return result


@user_router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    try:
        if not user_id or not check_uuid(user_id):
            raise HTTPException(
                status_code=400, detail="Please provide a valid user id"
            )

        user = database.query(User).filter_by(id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(
            status_code=200,
            content={
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "img_url": user.img_url,
                },
                "favorite_bots": [
                    {
                        "id": str(bot.id),
                        "name": bot.name,
                        "description": bot.description,
                        "avatar": bot.avatar,
                    }
                    for bot in user.favorite_bots
                ],
                "custom_bots": [
                    {
                        "id": str(bot.id),
                        "name": bot.name,
                        "description": bot.description,
                        "avatar": bot.avatar,
                    }
                    for bot in user.bots
                ],
                "chat_activity": [
                    {
                        "id": str(chat.id),
                        "name": chat.name,
                        "description": chat.description,
                    }
                    for chat in user.chats
                ],
            },
        )

    except HTTPException as http_execp:
        print("HTTPException in get_user_profile: ", str(http_execp))
        raise http_execp

    except Exception as e:
        print("Exception in get_user_profile: ", str(e))
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": "Internal server error"},
        )


@user_router.get("/credits/{user_id}")
async def user_credits(user_id):
    try:
        if not user_id or not check_uuid(user_id):
            raise HTTPException(
                status_code=400, detail="Please provide a valid user id"
            )

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
        return {"status": 500, "credits": None}
