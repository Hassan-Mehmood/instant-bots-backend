from fastapi import APIRouter, BackgroundTasks
from src.components.llm import LLM
from src.schemas.chat_schema import ChatRequestSchema, ResponseSchema
from src.components.ai_suite_client import AiSuiteClient

chat_router = APIRouter(prefix="/chat", tags=["chat"])
llm = LLM()
aiSuite = AiSuiteClient()

# @chat_router.post('/', response_model=ResponseSchema)
# async def root(req: RequestSchema):

#     # Add a proper error handling and logging system
#     if not req.message or not req.role or not req.user_id or not req.bot_id:
#         return ResponseSchema(response="Please provide message and role")


#     response = llm.chat(req.message, req.role, req.user_id, req.bot_id)

#     return ResponseSchema(response=response)


@chat_router.post("/", response_model=ResponseSchema)
async def root(req: ChatRequestSchema, background_tasks: BackgroundTasks):
    # Add a proper error handling and logging system
    if not req.message or not req.model or not req.user_id or not req.bot_id:
        return ResponseSchema(response="Please provide message and role")

    response = aiSuite.chat(
        bot_id=req.bot_id,
        user_id=req.user_id,
        message=req.message,
        model=req.model,
        chat_history=req.chat_history,
        background_tasks=background_tasks,
    )

    return ResponseSchema(role=response["role"], content=response["content"])
