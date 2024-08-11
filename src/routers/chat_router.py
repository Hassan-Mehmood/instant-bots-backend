from fastapi import APIRouter
from src.components.llm import LLM
from src.schemas.chat_schema import RequestSchema, ResponseSchema

chat_router = APIRouter(prefix='/chat')
llm = LLM()


@chat_router.post('/', response_model=ResponseSchema)
async def root(req: RequestSchema):
    
    # Add a proper error handling and logging system
    if not req.message or not req.role:
        return ResponseSchema(response="Please provide message and role")


    response = llm.chat(req.message, req.role)

    return ResponseSchema(response=response.content)