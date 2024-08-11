from pydantic import BaseModel


class RequestSchema(BaseModel):
    message: str
    role: str

class ResponseSchema(BaseModel):
    response: str

