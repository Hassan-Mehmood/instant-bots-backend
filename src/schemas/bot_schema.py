from pydantic import BaseModel


class BotRequestSchema(BaseModel):
    name: str
    description: str
    prompt: str
    price: int
    transactions: list
    chats: list

# class BotResponseSchema(BaseModel):
#     bot: str

