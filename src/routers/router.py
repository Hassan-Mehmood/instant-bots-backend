from fastapi.routing import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.models import User


router = APIRouter()


@router.get("/profile/{user_id}")
async def profile(user_id: str, db: Session = Depends(get_db)):
    """
    Get user profile by user_id.
    """

    user = db.query(User).filter(User.clerk_id == user_id).first()
    if not user:
        return JSONResponse(status_code=404, content={"message": "User not found"})

    return JSONResponse(
        status_code=200,
        content={
            "message": "User profile fetched successfully",
            "profile": {
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
                    }
                    for bot in user.favorite_bots
                ],
                "credits": user.credits,
                "custom_bots": [
                    {
                        "id": str(bot.id),
                        "name": bot.name,
                        "description": bot.description,
                    }
                    for bot in user.bots
                ],
            },
        },
    )
