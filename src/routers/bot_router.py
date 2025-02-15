from fastapi import APIRouter, HTTPException

from src.models.models import Bot, User
from src.db.database import SessionLocal

from src.schemas.bot_schema import (
    BotRequestSchema, 
    BotResponseSchema, 
    BotSchema, 
    BotsResponseSchema, 
    FavoriteBotRequestSchema
)

from src.models.utils import BotVisibility
from src.routers.utils import check_uuid

bot_router = APIRouter(prefix='/bots')
database = SessionLocal()

@bot_router.get("/all/{user_id}", response_model=BotsResponseSchema)
async def get_bots(user_id: str):
    try:
        if not user_id or not check_uuid(user_id):
            raise HTTPException(status_code=400, detail="Please provide a valid user id")

        data = (
            database.query(Bot)
            .filter((Bot.visibility == "PUBLIC") | (Bot.user_id == user_id))
            .all()
        )

        if not data:
            return BotsResponseSchema(bots=None, status=404, message="No bots found for the user")

        all_bots = [BotSchema.model_validate(bot) for bot in data]

        return BotsResponseSchema(bots=all_bots, status=200, message="Bots fetched successfully")
    
    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in get_bots: ", str(e))
        return BotResponseSchema(bot=None, status=500, message="Error fetching bots")

# #? Create a new bot
# @bot_router.post('/create', response_model=BotResponseSchema)
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


@bot_router.post('/create/{user_id}', response_model=BotResponseSchema)
async def create_bot(user_id: str, req: BotRequestSchema):
    try:
        name = req.name
        description = req.description
        prompt = req.prompt
        price = req.price
        type = req.type
        visibility = req.visibility.upper()

        if not name or not description or not prompt or price is None or not type or not visibility:
            raise HTTPException(status_code=400, detail="Please provide all required fields")
        
        if not check_uuid(user_id):
            raise HTTPException(status_code=400, detail="Please provide a valid user id")

        new_bot = Bot(
            name = name,
            description = description,
            prompt = prompt,
            price = price,
            type = type,
            visibility = BotVisibility(visibility),
            user_id = user_id
        )

        print("adding new bot:", new_bot)
        database.add(new_bot)
        print("commiting new bot")
        database.commit()
        database.refresh(new_bot)

        return BotResponseSchema(bot=BotSchema.model_validate(new_bot) , status=201, message="Bot created successfully")

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in create_bot: ", str(e))
        return BotResponseSchema(bot=None, status=500, message="Error creating bot", error=str(e))


#? Get a single bot by id
@bot_router.get('/{bot_id}', response_model=BotResponseSchema)
async def get_bot(bot_id: str):
    try:
        if not bot_id or not check_uuid(bot_id):
            raise HTTPException(status_code=400, detail="Please provide bot id")

        result = database.query(Bot).filter_by(id=bot_id).first()

        if not result:
            return BotResponseSchema(bot=None, status=404, message="Bot not found")

        return BotResponseSchema(bot=BotSchema.model_validate(result), status=200, message="Bot fetched successfully")
    
    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in get_bot: ", str(e))
        return BotResponseSchema(bot=None, status=500, message="Error fetching bot")

#? Delete a single bot by id
@bot_router.delete('/{bot_id}', response_model=BotResponseSchema)
async def delete_bot(bot_id: str):
    try:
        if not bot_id or not check_uuid(bot_id):
            raise HTTPException(status_code=400, detail="Please provide bot id")

        result = database.query(Bot).filter_by(id=bot_id).first()

        if not result:
            return BotResponseSchema(bot=None, status=404, message="Bot not found")

        database.delete(result)
        database.commit()

        return BotResponseSchema(bot=BotSchema.model_validate(result), status=200, message="Bot deleted successfully")
    
    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in delete_bot: ", str(e))
        return BotResponseSchema(bot=None, status=500, message="Error deleting bot")

#? Update a single bot by id
@bot_router.put('/{bot_id}', response_model=BotResponseSchema)
async def update_bot(bot_id: str, req: BotRequestSchema):
    try:
        if not bot_id or not check_uuid(bot_id):
            raise HTTPException(status_code=400, detail="Please provide bot id")

        result = database.query(Bot).filter_by(id=bot_id).first()

        if not result:
            return BotResponseSchema(bot=None, status=404, message="Bot not found")

        result.name = req.name
        result.description = req.description
        result.prompt = req.prompt
        result.price = req.price
        result.type = req.type

        database.commit()
        database.refresh(result)

        return BotResponseSchema(bot=BotSchema.model_validate(result), status=200, message="Bot updated successfully")
    except Exception as e:
        print("Exception in update_bot: ", str(e))
        return BotResponseSchema(bot=None, status=500, message="Error updating bot")


@bot_router.post('/add-favourite', response_model=BotResponseSchema)
async def add_favourite_bot(req: FavoriteBotRequestSchema):
    try:
        user_id = req.user_id
        bot_id = req.bot_id

        if not check_uuid(user_id) or not check_uuid(bot_id):
            raise HTTPException(status_code=400, detail="Please provide valid user id and bot id")

        if not user_id or not bot_id:
            raise HTTPException(status_code=400, detail="Please provide user id and bot id")

        bot = database.query(Bot).filter_by(id=bot_id).first()

        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        user = database.query(User).filter_by(id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        #? Check if bot is owned by user and visibility is private
        #? If bot is not owned by user and visibility is private, return error
        if bot.visibility == BotVisibility.PRIVATE and bot.user_id != user.id:
            raise HTTPException(status_code=403, detail="Bot is private and not owned by user")

        if bot in user.favorite_bots:
            raise HTTPException(status_code=400, detail="Bot already added to favourites")

        user.favorite_bots.append(bot)
        database.commit()

        return BotResponseSchema(bot=BotSchema.model_validate(bot), status=200, message="Bot added to favourites successfully")

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in add_favourite_bot: ", str(e))
        raise HTTPException(status_code=500, detail="Error adding bot to favourites")
    
@bot_router.post('/remove-favourite', response_model=BotResponseSchema)
async def remove_favourite_bot(req: FavoriteBotRequestSchema):
    try:
        user_id = req.user_id
        bot_id = req.bot_id

        if not check_uuid(user_id) or not check_uuid(bot_id):
            raise HTTPException(status_code=400, detail="Please provide valid user id and bot id")

        if not user_id or not bot_id:
            raise HTTPException(status_code=400, detail="Please provide user id and bot id")

        bot = database.query(Bot).filter_by(id=bot_id).first()

        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        user = database.query(User).filter_by(id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if bot not in user.favorite_bots:
            raise HTTPException(status_code=400, detail="Bot not added to favourites")

        user.favorite_bots.remove(bot)
        database.commit()

        return BotResponseSchema(bot=BotSchema.model_validate(bot), status=200, message="Bot removed from favourites successfully")

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in remove_favourite_bot: ", str(e))
        raise HTTPException(status_code=500, detail="Error removing bot from favourites")
    

@bot_router.get('/favourite-bots/{user_id}', response_model=BotsResponseSchema)
async def get_favourite_bots(user_id: str):
    try:

        if not user_id or not check_uuid(user_id):
            raise HTTPException(status_code=400, detail="Please provide a valid user id")
        
        user = database.query(User).filter_by(id=user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return BotsResponseSchema(bots=[BotSchema.model_validate(bot) for bot in user.favorite_bots], status=200, message="Favourite bots fetched successfully")

    except HTTPException as http_execp:
        raise http_execp

    except Exception as e:
        print("Exception in get_favourite_bots: ", str(e))
        raise HTTPException(status_code=500, detail="Error fetching favourite bots")