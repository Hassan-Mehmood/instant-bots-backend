from fastapi import APIRouter, BackgroundTasks
from src.components.llm import LLM
from src.schemas.chat_schema import ChatRequestSchema, ResponseSchema
from src.components.ai_suite_client import AiSuiteClient
from src.models.models import Chat

from src.db.database import SessionLocal
from sqlalchemy.orm import Session


chat_router = APIRouter(prefix="/chat", tags=["chat"])
llm = LLM()
aiSuite = AiSuiteClient()


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
    # user_id: c2c4c22c-b98d-43fb-b33d-d42dd0df6187
    # bot_id:  59d90193-b0c7-497d-9f50-14b0ae441c47

    return ResponseSchema(role=response["role"], content=response["content"])


@chat_router.get("/{user_id}/{bot_id}")
async def get_chat_history(user_id: str, bot_id: str):
    """
    Retrieve chat history for a specific bot and user.
    """
    try:
        db: Session = SessionLocal()

        chat = db.query(Chat).filter_by(bot_id=bot_id, user_id=user_id).first()

        if not chat:
            return {"chat_history": []}

        chat_history = []
        for message in chat.messages:
            chat_history.append(
                {"id": message.id, "role": message.sender, "content": message.content}
            )

        return {"chat_history": chat_history}
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return {"error": "An error occurred while retrieving chat history."}


# delete
@chat_router.delete("/{user_id}/{bot_id}")
async def delete_chat_history(user_id: str, bot_id: str):
    """
    Delete chat history for a specific bot and user.
    """
    try:
        db: Session = SessionLocal()

        chat = db.query(Chat).filter_by(bot_id=bot_id, user_id=user_id).first()

        if not chat:
            return {"message": "No chat history found for this user and bot."}

        db.delete(chat)
        db.commit()

        return {"message": "Chat history deleted successfully."}
    except Exception as e:
        print(f"Error deleting chat history: {e}")
        return {"error": "An error occurred while deleting chat history."}
