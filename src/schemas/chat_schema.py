from pydantic import BaseModel


class ChatRequestSchema(BaseModel):
    message: str
    model:str
    chat_history: list = []
    user_id: str
    bot_id: str

class ResponseSchema(BaseModel):
    role: str
    content: str

