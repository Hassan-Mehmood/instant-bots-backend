from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Depends

from src.models.models import Bot, User

from src.schemas.bot_schema import (
    BotRequestSchema,
    FavoriteBotRequestSchema,
    UpdateBotRequestSchema,
)

from src.models.utils import BotVisibility
from src.routers.utils import check_uuid
from sqlalchemy.orm import Session
from src.db.database import get_db


bot_router = APIRouter(prefix="/bots", tags=["bots"])
database = None


# all bots for a user
@bot_router.get("/all/{user_id}")
async def get_bots(user_id: str, db: Session = Depends(get_db)):
    try:
        data = (
            db.query(Bot)
            .filter((Bot.visibility == "PUBLIC") | (Bot.user_id == user_id))
            .all()
        )

        if not data:
            return JSONResponse(
                status_code=404, content={"message": "No bots found for the user"}
            )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Bots fetched successfully",
                "bots": [
                    {
                        "id": str(bot.id),
                        "name": bot.name,
                        "description": bot.description,
                        "prompt": bot.prompt,
                        "avatar": bot.avatar,
                        "visibility": bot.visibility,
                        "created_at": bot.created_at.isoformat(),
                        "updated_at": bot.updated_at.isoformat(),
                    }
                    for bot in data
                ],
            },
        )

    except HTTPException as http_execp:
        print("HTTPException in get_bots: ", str(http_execp))
        raise http_execp

    except Exception as e:
        print("Exception in get_bots: ", str(e))
        return JSONResponse(status_code=500, content={"message": "Error fetching bots"})


# #? Create a new bot
# @bot_router.post('/create')
# async def create_bot(req: BotRequestSchema):
#     try:
#         name = req.name
#         description = req.description
#         prompt = req.prompt
#         price = req.price
#         type = req.type
#         visibility = req.visibility

#         if not name or not description or not prompt or price is None or not type or not visibility:
#             raise HTTPException(status_code=400, detail="Please provide all required fields")

#         new_bot = Bot(
#             name = name,
#             description = description,
#             prompt = prompt,
#             price = price,
#             type = type,
#             visibility = visibility
#         )

#         print("adding new bot")
#         database.add(new_bot)
#         print("commiting new bot")
#         database.commit()
#         database.refresh(new_bot)

#         return BotResponseSchema(bot=BotSchema.model_validate(new_bot) , status=201, message="Bot created successfully")

#     except HTTPException as http_execp:
#         raise http_execp

#     except Exception as e:
#         print("Exception in create_bot: ", str(e))
#         return BotResponseSchema(bot=None, status=500, message="Error creating bot")


@bot_router.post("/create/{user_id}")
async def create_bot(
    user_id: str, req: BotRequestSchema, db: Session = Depends(get_db)
):
    try:
        name = req.name
        description = req.description
        prompt = req.prompt
        visibility = req.visibility

        # if not check_uuid(user_id):
        #     raise HTTPException(
        #         status_code=400, detail="Please provide a valid user id"
        #     )

        new_bot = Bot(
            name=name,
            description=description,
            prompt=prompt,
            user_id=user_id,
            visibility=visibility,
        )

        print("adding new bot:")
        db.add(new_bot)
        print("commiting new bot")
        db.commit()

        return JSONResponse(
            status_code=201,
            content={
                "message": "Bot created successfully",
                "data": {
                    "id": str(new_bot.id),
                    "name": new_bot.name,
                    "description": new_bot.description,
                    "prompt": new_bot.prompt,
                    "avatar": new_bot.avatar,
                    "user_id": str(new_bot.user_id),
                    "visibility": new_bot.visibility,
                    "created_at": new_bot.created_at.isoformat(),
                    "updated_at": new_bot.updated_at.isoformat(),
                },
            },
        )

    except HTTPException as http_execp:
        print("HTTPException in create_bot: ", str(http_execp))
        raise http_execp

    except Exception as e:
        print("Exception in create_bot: ", str(e))
        return JSONResponse(status_code=500, content={"message": "Error creating bot"})


# ? Get a single bot by id
@bot_router.get("/get/{bot_id}")
async def get_bot(bot_id: str, db: Session = Depends(get_db)):
    try:
        if not bot_id or not check_uuid(bot_id):
            raise HTTPException(status_code=400, detail="Please provide bot id")

        bot = db.query(Bot).filter_by(id=bot_id).first()

        if not bot:
            return JSONResponse(status_code=404, content={"message": "Bot not found"})

        return JSONResponse(
            status_code=200,
            content={
                "message": "Bot fetched successfully",
                "data": {
                    "id": str(bot.id),
                    "name": bot.name,
                    "description": bot.description,
                    "prompt": bot.prompt,
                    "avatar": bot.avatar,
                    "visibility": bot.visibility,
                    "created_at": bot.created_at.isoformat(),
                    "updated_at": bot.updated_at.isoformat(),
                },
            },
        )

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in get_bot: ", str(e))
        return JSONResponse(status_code=500, content={"message": "Error fetching bot"})


# ? Delete a single bot by id
@bot_router.delete("/delete/{bot_id}")
async def delete_bot(bot_id: str, db: Session = Depends(get_db)):
    try:
        if not bot_id or not check_uuid(bot_id):
            raise HTTPException(status_code=400, detail="Please provide bot id")

        bot = db.query(Bot).filter_by(id=bot_id).first()

        if not bot:
            return JSONResponse(status_code=404, content={"message": "Bot not found"})

        db.delete(bot)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={"message": "Bot deleted successfully"},
        )

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in delete_bot: ", str(e))
        return JSONResponse(status_code=500, content={"message": "Error deleting bot"})


# ? Update a single bot by id
@bot_router.patch("/update/{bot_id}")
async def update_bot(
    bot_id: str, req: UpdateBotRequestSchema, db: Session = Depends(get_db)
):
    try:
        if not bot_id or not check_uuid(bot_id):
            raise HTTPException(status_code=400, detail="Please provide bot id")

        bot = db.query(Bot).filter_by(id=bot_id).first()

        if not bot:
            return JSONResponse(status_code=404, content={"message": "Bot not found"})

        if req.name:
            bot.name = req.name

        if req.description:
            bot.description = req.description

        if req.prompt:
            bot.prompt = req.prompt

        if req.avatar:
            bot.avatar = req.avatar

        db.commit()
        db.refresh(bot)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Bot updated successfully",
                "data": {
                    "id": str(bot.id),
                    "name": bot.name,
                    "description": bot.description,
                    "prompt": bot.prompt,
                    "avatar": bot.avatar,
                    "created_at": bot.created_at.isoformat(),
                    "updated_at": bot.updated_at.isoformat(),
                },
            },
        )
    except Exception as e:
        print("Exception in update_bot: ", str(e))
        return JSONResponse(status_code=500, content={"message": "Error updating bot"})


@bot_router.post("/add-favourite")
async def add_favourite_bot(
    req: FavoriteBotRequestSchema, db: Session = Depends(get_db)
):
    try:
        user_id = req.userId
        bot_id = req.botId

        if not check_uuid(bot_id):
            raise HTTPException(
                status_code=400, detail="Please provide valid user id and bot id"
            )

        if not user_id or not bot_id:
            raise HTTPException(
                status_code=400, detail="Please provide user id and bot id"
            )

        bot = db.query(Bot).filter_by(id=bot_id).first()

        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        user = db.query(User).filter_by(clerk_id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ? Check if bot is owned by user and visibility is private
        # ? If bot is not owned by user and visibility is private, return error
        if (
            bot.visibility == BotVisibility.PRIVATE.value
            and bot.user_id != user.clerk_id
        ):
            raise HTTPException(
                status_code=403, detail="Bot is private and not owned by user"
            )

        if bot in user.favorite_bots:
            return JSONResponse(
                status_code=400,
                content={"message": "Bot already added to favourites"},
            )

        user.favorite_bots.append(bot)
        print("Adding bot to user's favourites")
        print("Committing changes to database")
        db.commit()

        return JSONResponse(
            status_code=200,
            content={
                "message": "Bot added to favourites successfully",
            },
        )

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in add_favourite_bot: ", str(e))
        raise HTTPException(status_code=500, detail="Error adding bot to favourites")


@bot_router.post("/remove-favourite")
async def remove_favourite_bot(
    req: FavoriteBotRequestSchema, db: Session = Depends(get_db)
):
    try:
        user_id = req.userId
        bot_id = req.botId

        if not check_uuid(bot_id):
            raise HTTPException(
                status_code=400, detail="Please provide valid user id and bot id"
            )

        if not user_id or not bot_id:
            raise HTTPException(
                status_code=400, detail="Please provide user id and bot id"
            )

        bot = db.query(Bot).filter_by(id=bot_id).first()

        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        user = db.query(User).filter_by(clerk_id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if bot not in user.favorite_bots:
            raise HTTPException(status_code=400, detail="Bot not added to favourites")

        user.favorite_bots.remove(bot)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={
                "message": "Bot removed from favourites successfully",
            },
        )

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in remove_favourite_bot: ", str(e))
        raise HTTPException(
            status_code=500, detail="Error removing bot from favourites"
        )


@bot_router.get("/favourite-bots/{user_id}")
async def get_favourite_bots(user_id: str, db: Session = Depends(get_db)):
    try:
        if not user_id:
            raise HTTPException(
                status_code=400, detail="Please provide a valid user id"
            )

        user = db.query(User).filter_by(clerk_id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(
            status_code=200,
            content={
                "message": "Favourite bots fetched successfully",
                "favorites": [
                    {
                        "id": str(bot.id),
                        "name": bot.name,
                        "description": bot.description,
                        "prompt": bot.prompt,
                        "avatar": bot.avatar,
                        "created_at": bot.created_at.isoformat(),
                        "updated_at": bot.updated_at.isoformat(),
                    }
                    for bot in user.favorite_bots
                ],
            },
        )

    except HTTPException as http_execp:
        print("HTTPException in get_favourite_bots: ", str(http_execp))
        raise http_execp

    except Exception as e:
        print("Exception in get_favourite_bots: ", str(e))
        return JSONResponse(
            status_code=500, content={"message": "Error fetching favourite bots"}
        )
