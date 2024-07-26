from pydantic import BaseModel


class RequestModal(BaseModel):
    message: str

class ResponseModal(BaseModel):
    response: str

