from pydantic import BaseModel
from typing import Optional, List
from src.models.models import Bot
from uuid import UUID


class BotSchema(BaseModel):
    id: UUID
    name: str
    description: str
    prompt: str
    price: int
    type: str
    visibility: str

    class Config:
        from_attributes = True  # This enables SQLAlchemy to Pydantic conversion


class BotRequestSchema(BaseModel):
    name: str
    description: str
    prompt: str
    price: int
    type: str
    visibility: str

class BotsResponseSchema(BaseModel):
    bot: Optional[List[BotSchema]]
    status: int
    message: str

class BotResponseSchema(BaseModel):
    bot: Optional[BotSchema]
    status: int
    message: str