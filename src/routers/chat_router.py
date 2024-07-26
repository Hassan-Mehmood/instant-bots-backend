from fastapi import APIRouter
from src.components.llm import LLM
from src.models.chat_models import RequestModal, ResponseModal

chat_router = APIRouter(prefix='/chat')
llm = LLM()

@chat_router.get("/")
async def root():
    return {"message": "Chat Router!"}


@chat_router.post('/', response_model=ResponseModal)
def root(req: RequestModal):
    print(req)
    response = llm.chat(req.message)

    return ResponseModal(response=response.content)