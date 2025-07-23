from pydantic import BaseModel
from typing import List
from uuid import UUID


class BotSchema(BaseModel):
    id: UUID
    name: str
    description: str
    prompt: str
    avatar: str
    visibility: str

    class Config:
        from_attributes = True  # This enables SQLAlchemy to Pydantic conversion


class BotRequestSchema(BaseModel):
    name: str
    description: str
    prompt: str
    visibility: str
    avatar: str


class UpdateBotRequestSchema(BaseModel):
    name: str = None
    description: str = None
    prompt: str = None
    avatar: str = None


class FavoriteBotRequestSchema(BaseModel):
    userId: str
    botId: str


class BuyBotRequestSchema(BaseModel):
    userId: str
    botId: str


class BotsResponseSchema(BaseModel):
    bots: List[BotSchema] = []
    status: int
    message: str
