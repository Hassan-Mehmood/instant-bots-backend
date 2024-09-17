from pydantic import BaseModel


class RequestSchema(BaseModel):
    message: str
    role: str
    user_id: str
    bot_id: str

class ResponseSchema(BaseModel):
    response: str

