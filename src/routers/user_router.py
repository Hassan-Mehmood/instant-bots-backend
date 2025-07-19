from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.models.models import Chat, User
from src.db.database import SessionLocal


user_router = APIRouter(prefix="/users", tags=["users"])

database = SessionLocal()


@user_router.get("/chats/{user_id}")
async def get_chats(user_id: str):
    if not user_id or user_id == "undefined":
        return

    result = database.query(Chat).filter_by(user_id=user_id)

    if not result:
        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "message": "No chats found for this user",
                "chats": [],
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": 200,
            "message": "Chats retrieved successfully",
            "chats": [
                {
                    "id": str(chat.id),
                    "name": chat.name,
                    "bot": {
                        "id": str(chat.bot.id),
                        "name": chat.bot.name,
                        "description": chat.bot.description,
                        # "avatar": chat.bot.avatar,
                    },
                    "user_id": str(chat.user_id),
                    "created_at": chat.created_at.isoformat(),
                    "updated_at": chat.updated_at.isoformat(),
                }
                for chat in result
            ],
        },
    )


@user_router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    try:
        if not user_id:
            raise HTTPException(
                status_code=400, detail="Please provide a valid user id"
            )

        user = database.query(User).filter_by(clerk_id=user_id).first()

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
                    "credits": user.credits,
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
        if not user_id:
            raise HTTPException(
                status_code=400, detail="Please provide a valid user id"
            )

        user = database.query(User).filter_by(clerk_id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.credits is None:
            user.credits = 0  # type: ignore

        return JSONResponse(
            status_code=200,
            content={
                "credits": user.credits,
            },
        )

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in user_credits: ", str(e))
        return {"status": 500, "credits": None}


@user_router.get("/transaction-history/{user_id}")
async def transaction_history(user_id: str):
    try:
        if not user_id:
            raise HTTPException(
                status_code=400, detail="Please provide a valid user id"
            )

        user = database.query(User).filter_by(clerk_id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.transactions is None:
            user.transactions = []  # type: ignore

        return JSONResponse(
            status_code=200,
            content={
                "transaction_history": [
                    {
                        "id": str(transaction.id),
                        "amount": transaction.amount,
                        "type": transaction.type,
                    }
                    for transaction in user.transactions
                ],
            },
        )

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in transaction_history: ", str(e))
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": "Internal server error"},
        )
