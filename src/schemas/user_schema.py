from pydantic import BaseModel
from typing import List
from src.models.models import User, Chat, Message

class messages(BaseModel):
    chat_id: str
    id: str
    sender: str
    content: str
    updated_at: str
    created_at: str

class Bot(BaseModel):
    id: str
    name: str
    description: str
    prompt: str
    price: int
    created_at: str
    updated_at: str

class UserGetAllChatsResponseItem(BaseModel):
    user_id: str
    bot_id: str
    created_at: str
    id: str
    updated_at: str
    messages: list
    


class UserGetAllChatsResponse(BaseModel):
    user_id : str
    bot_id : str
    created_at : str
    id : str
    updated_at : str
    bot: Bot
    messages: List[messages]


class UserGetAllChatsRequest(BaseModel):
    user_id: str

