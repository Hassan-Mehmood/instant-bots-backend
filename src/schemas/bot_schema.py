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


class UpdateBotRequestSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    prompt: str | None = None
    avatar: str | None = None


class BotsResponseSchema(BaseModel):
    bots: List[BotSchema] = []
    status: int
    message: str


class FavoriteBotRequestSchema(BaseModel):
    botId: str
    userId: str
