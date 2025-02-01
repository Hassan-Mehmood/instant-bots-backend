from fastapi import APIRouter
from src.models.models import Bot
from src.db.database import SessionLocal

from src.schemas.bot_schema import CreateBotRequestSchema, CreateBotResponseSchema, BotSchema



from sqlalchemy.orm import joinedload
from sqlalchemy import select

bot_router = APIRouter(prefix='/bot')
database = SessionLocal()

@bot_router.get("/all")
async def get_chats():
    result = database.query(Bot).all()

    return result


@bot_router.post('/create', response_model=CreateBotResponseSchema)
async def create_bot(req: CreateBotRequestSchema):
    try:
        name = req.name
        description = req.description
        prompt = req.prompt
        price = req.price
        type = req.type

        if not name or not description or not prompt or not price or not type:
            return CreateBotResponseSchema(bot=None, status=400, message="Please provide all required fields")

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

        return CreateBotResponseSchema(bot=BotSchema.model_validate(new_bot) , status=201, message="Bot created successfully")

    except Exception as e:
        print("Exception in create_bot: ", str(e))
        return CreateBotResponseSchema(bot=None, status=500, message="Error creating bot")


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