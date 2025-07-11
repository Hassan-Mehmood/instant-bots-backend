import os
import base64
from typing import Optional, Any, Dict, List
import fitz

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.db.database import SessionLocal
from src.models.models import Bot, Chat, Message
from src.routers.utils import check_uuid
from src.models.utils import MessageSender
from src.components.file_upload import upload_file

load_dotenv()

MODELS = {
    "gpt-4o": "openai",
    "gpt-4.1": "openai",
    "gpt-4.1-mini": "openai",
    "gpt-4o-mini": "openai",
    "gemma2-9b-it": "groq",
    "groq-1.5": "groq",
    "llama-3.1-8b-instant": "groq",
    "llama-3.3-70b-versatile": "groq",
    "meta-llama/llama-guard-4-12b": "groq",
    "gemini-2.0-flash": "google_genai",
    "gemini-2.0-pro": "google_genai",
    "gemini-2.5-flash": "google_genai",
    "gemini-2.5-pro": "google_genai",
}


class ModelClient:
    def __init__(self, model_name):
        self.load_api_keys()
        print("Loading model:", model_name)
        self.model = init_chat_model(
            model=model_name, model_provider=MODELS.get(model_name)
        )

    def load_api_keys(self):
        os.getenv("OPENAI_API_KEY")
        os.getenv("GROQ_API_KEY")
        os.getenv("GOOGLE_API_KEY")

    async def chat(
        self,
        message: str,
        user_id: str,
        bot_id: str,
        model: str,
        chat_history: list,
        file: Optional[UploadFile] = None,
    ) -> dict:
        file_url = None
        if not message or not model:
            raise HTTPException(
                status_code=400, detail="Please provide model and message"
            )

        if not check_uuid(bot_id):
            raise HTTPException(
                status_code=400, detail="Please provide valid and bot id"
            )

        if model not in MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model. Available models: {', '.join(MODELS.keys())}",
            )

        with SessionLocal() as db:
            bot = (
                db.query(Bot)
                .filter(
                    Bot.id == bot_id,
                    ((Bot.visibility == "PUBLIC") | (Bot.user_id == user_id)),
                )
                .first()
            )

            if not bot:
                raise HTTPException(status_code=404, detail="Bot not found")

            prompt = bot.prompt

        user_message_content: List[Dict[str, Any]] = [{"type": "text", "text": message}]

        if file:
            print("File received")
            if file.content_type and file.content_type.startswith("image/"):
                try:
                    print("Image file")
                    file_content = await file.read()
                    base64_image = base64.b64encode(file_content).decode("utf-8")
                    image_url = f"data:{file.content_type};base64,{base64_image}"
                    user_message_content.append(
                        {"type": "image_url", "image_url": {"url": image_url}}
                    )
                except Exception as e:
                    print(f"Error processing image: {e}")
                    return {
                        "role": "assistant",
                        "content": "Error processing image",
                    }
            elif file.content_type == "application/pdf":
                print("PDF file")
                try:
                    pdf_content = await file.read()
                    doc = fitz.open(stream=pdf_content, filetype="pdf")
                    pdf_text = ""
                    for page in doc:
                        pdf_text += page.get_text()  # type: ignore
                    doc.close()
                    user_message_content[0]["text"] += (
                        f"\n\n--- PDF Content ---\n{pdf_text}"
                    )

                    print("PDF text:", pdf_text)
                except Exception as e:
                    print(f"Error processing PDF: {e}")
                    return {
                        "role": "assistant",
                        "content": "Error processing PDF",
                    }
            else:
                print("Other file")
                try:
                    file_text = (await file.read()).decode("utf-8")
                    user_message_content[0]["text"] += (
                        f"\n\n--- File Content ---\n{file_text}"
                    )
                except Exception:
                    return {
                        "role": "assistant",
                        "content": "Error processing file",
                    }
            file.file.seek(0)
            file_url = await upload_file(file)
            print("File URL:", file_url)

        messages = [
            SystemMessage(str(prompt)),
            *[
                HumanMessage(content=msg["content"])
                if msg.get("role") == "user"
                else AIMessage(content=msg["content"])
                for msg in chat_history
            ],
            HumanMessage(content=user_message_content),  # type: ignore
        ]

        response_content = ""
        try:
            response = await self.model.ainvoke(messages)
            response_content = str(response.content)
        except Exception as e:
            print("Error generating chat completion: ", str(e))
            raise HTTPException(
                status_code=500, detail="Error generating chat response"
            )
        finally:
            self.store_message(
                bot_id, user_id, message, "user", file_url if file_url else None
            )
            if response_content:
                self.store_message(bot_id, user_id, response_content, "assistant", None)

            return {
                "role": "assistant",
                "content": response_content,
            }

    def store_message(
        self,
        bot_id: str,
        user_id: str,
        message: str,
        sender: str,
        file_path: Optional[str] = None,
    ) -> None:
        db: Session = SessionLocal()
        chat = None
        try:
            chat = db.query(Chat).filter_by(bot_id=bot_id, user_id=user_id).first()

            if not chat and sender == "user":
                print("Chat not found")

                response = self.model.invoke(
                    [
                        SystemMessage(
                            """ You are responsible for naming the chats between users and bots. You will be given first message of the chat and you need to come up with a name for the chat.
                            Choose an appropraite name for the chat based on the user's message. 
                            The name should be concise and relevant to the conversation.
                            Your response should only contain the name of the chat without any additional text."""
                        ),
                        HumanMessage(content=message),
                    ]
                )

                print("Chat Name:", response.content)

                name = response.content

                chat = Chat(bot_id=bot_id, user_id=user_id, name=name)
                print("Creating new chat with name:", name)

                db.add(chat)
                db.flush()

            if chat:
                new_message = Message(
                    chat_id=chat.id,
                    content=message,
                    sender=MessageSender(sender).value,
                    file_path=file_path,
                )

                db.add(new_message)
                db.commit()
                print("Stored message")

        except Exception as e:
            db.rollback()
            print("Error storing message", str(e))

        finally:
            db.close()
