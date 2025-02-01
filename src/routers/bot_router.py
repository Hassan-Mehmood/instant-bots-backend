from fastapi import APIRouter
from src.models.models import Bot
from src.db.database import SessionLocal

from src.schemas.bot_schema import BotRequestSchema, BotResponseSchema, BotSchema



from sqlalchemy.orm import joinedload
from sqlalchemy import select

bot_router = APIRouter(prefix='/bot')
database = SessionLocal()

@bot_router.get("/all")
async def get_chats():
    result = database.query(Bot).all()

    return result

#? Create a new bot
@bot_router.post('/create', response_model=BotResponseSchema)
async def create_bot(req: BotRequestSchema):
    try:
        name = req.name
        description = req.description
        prompt = req.prompt
        price = req.price
        type = req.type

        if not name or not description or not prompt or price is None or not type:
            return BotResponseSchema(bot=None, status=400, message="Please provide all required fields")

        new_bot = Bot(
            name = name,
            description = description,
            prompt = prompt,
            price = price,
            type = type,
        )

        print("adding new bot")
        database.add(new_bot)
        print("commiting new bot")
        database.commit()
        database.refresh(new_bot)

        return BotResponseSchema(bot=BotSchema.model_validate(new_bot) , status=201, message="Bot created successfully")

    except Exception as e:
        print("Exception in create_bot: ", str(e))
        return BotResponseSchema(bot=None, status=500, message="Error creating bot")

#? Get a single bot by id
@bot_router.get('/{bot_id}', response_model=BotResponseSchema)
async def get_bot(bot_id: str):
    try:
        if not bot_id:
            return BotResponseSchema(bot=None, status=400, message="Please provide bot id")

        result = database.query(Bot).filter_by(id=bot_id).first()

        if not result:
            return BotResponseSchema(bot=None, status=404, message="Bot not found")

        return BotResponseSchema(bot=BotSchema.model_validate(result), status=200, message="Bot fetched successfully")
    except Exception as e:
        print("Exception in get_bot: ", str(e))
        return BotResponseSchema(bot=None, status=500, message="Error fetching bot")

#? Delete a single bot by id
@bot_router.delete('/{bot_id}', response_model=BotResponseSchema)
async def delete_bot(bot_id: str):
    try:
        if not bot_id:
            return BotResponseSchema(bot=None, status=400, message="Please provide bot id")

        result = database.query(Bot).filter_by(id=bot_id).first()

        if not result:
            return BotResponseSchema(bot=None, status=404, message="Bot not found")

        database.delete(result)
        database.commit()

        return BotResponseSchema(bot=BotSchema.model_validate(result), status=200, message="Bot deleted successfully")
    except Exception as e:
        print("Exception in delete_bot: ", str(e))
        return BotResponseSchema(bot=None, status=500, message="Error deleting bot")

#? Update a single bot by id
@bot_router.put('/{bot_id}', response_model=BotResponseSchema)
async def update_bot(bot_id: str, req: BotRequestSchema):
    try:
        if not bot_id:
            return BotResponseSchema(bot=None, status=400, message="Please provide bot id")

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

# @app.post('/bot/create')
# async def create_bot(req: BotRequestSchema):

#     print(req.name)
#     print(req.description)
#     print(req.prompt)
#     print(req.price)
#     print(req.transactions)
#     print(req.chats)

#     session = SessionLocal()

#     bot = Bot(
#         id = str(uuid4()),
#         name = req.name,
#         description = req.description,
#         prompt = req.prompt,
#         price = req.price,
#         transactions = req.transactions,
#         chats = req.chats
#     )

#     session.add(bot)
#     session.commit()
#     session.refresh(bot)

#     return bot