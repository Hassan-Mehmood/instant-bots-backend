from fastapi import APIRouter, BackgroundTasks, Form, File, UploadFile
from src.schemas.chat_schema import ResponseSchema
from src.components.model import ModelClient
from src.models.models import Chat

from src.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import Optional
import json


chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post("/", response_model=ResponseSchema)
async def root(
    message: str = Form(...),
    model: str = Form(...),
    user_id: str = Form(...),
    bot_id: str = Form(...),
    chat_history: str = Form("[]"),
    file: Optional[UploadFile] = File(None),
):
    if not message or not model or not user_id or not bot_id:
        return ResponseSchema(
            role="assistant", content="Please provide all required fields."
        )
    if file:
        print("File received")

    model_client = ModelClient(model_name=model)

    parsed_chat_history = json.loads(chat_history)

    response = await model_client.chat(
        bot_id=bot_id,
        user_id=user_id,
        message=message,
        model=model,
        chat_history=parsed_chat_history,
        file=file,
    )

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
