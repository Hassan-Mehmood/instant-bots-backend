import os

from fastapi import HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.db.database import SessionLocal
from src.models.models import Bot, Chat, Message
from src.routers.utils import check_uuid
from src.models.utils import MessageSender

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

    def chat(
        self,
        message: str,
        user_id: str,
        bot_id: str,
        model: str,
        chat_history: list,
    ) -> dict:
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

        updated_history = chat_history.copy()
        updated_history.append({"role": "user", "content": message})

        messages = [
            SystemMessage(prompt),
            *[
                HumanMessage(content=msg["content"])
                if msg.get("role") == "user"
                else AIMessage(content=msg["content"])
                for msg in updated_history
            ],
        ]

        try:
            response = self.model.invoke(messages)

        except Exception as e:
            print("Error generating chat completion: ", str(e))
            raise HTTPException(
                status_code=500, detail="Error generating chat response"
            )

        finally:
            self.store_message(bot_id, user_id, message, "user")
            self.store_message(bot_id, user_id, response.content, "assistant")

            return {
                "role": "assistant",
                "content": response.content,
            }

    def store_message(
        self,
        bot_id: str,
        user_id: str,
        message: str,
        sender: str,
    ) -> None:
        db: Session = SessionLocal()

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

            new_message = Message(
                chat_id=chat.id, content=message, sender=MessageSender(sender).value
            )

            db.add(new_message)
            db.commit()
            print("Stored message")

        except Exception as e:
            db.rollback()
            print("Error storing message", str(e))

        finally:
            db.close()
