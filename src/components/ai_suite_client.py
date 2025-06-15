import os

from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import aisuite as ai
from src.db.database import SessionLocal
from src.models.models import Bot, Chat, Message
from src.routers.utils import check_uuid
from src.models.utils import MessageSender

load_dotenv()


class AiSuiteClient:
    def __init__(self):
        self.load_api_keys()
        self.client = ai.Client()

    def load_api_keys(self):
        os.getenv("OPENAI_API_KEY")
        os.getenv("ANTHROPIC_API_KEY")
        os.getenv("GROQ_API_KEY")

    def chat(
        self,
        message: str,
        user_id: str,
        bot_id: str,
        model: str,
        chat_history: list,
        background_tasks: BackgroundTasks,
    ) -> dict:
        if not message or not model:
            raise HTTPException(
                status_code=400, detail="Please provide model and message"
            )

        if not check_uuid(bot_id):
            raise HTTPException(
                status_code=400, detail="Please provide valid and bot id"
            )

        with SessionLocal() as db:
            bot = db.query(Bot).filter_by(id=bot_id, user_id=user_id).first()

            if not bot:
                raise HTTPException(status_code=404, detail="Bot not found")

            prompt = bot.prompt

        updated_history = chat_history.copy()
        updated_history.insert(0, {"role": "system", "content": prompt})
        updated_history.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=model, messages=updated_history
            )

        except Exception as e:
            print("Error generating chat completion: ", str(e))
            raise HTTPException(
                status_code=500, detail="Error generating chat response"
            )

        # background_tasks.add_task(
        #     self.store_message, bot_id, user_id, message, "USER", model
        # )
        # background_tasks.add_task(
        #     self.store_message,
        #     bot_id,
        #     user_id,
        #     response.choices[0].message.content,
        #     "BOT",
        #     model,
        # )

        self.store_message(bot_id, user_id, message, "USER", model)
        self.store_message(
            bot_id, user_id, response.choices[0].message.content, "BOT", model
        )
        print("Stored messages")

        return {"role": "assistant", "content": response.choices[0].message.content}

    def store_message(
        self, bot_id: str, user_id: str, message: str, sender: str, model: str
    ) -> None:
        db: Session = SessionLocal()

        try:
            chat = db.query(Chat).filter_by(bot_id=bot_id, user_id=user_id).first()

            if not chat and sender == "USER":
                print("Chat not found")

                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Choose a approriate name for the chat",
                        },
                        {"role": "user", "content": message},
                    ],
                )

                name = response.choices[0].message.content

                chat = Chat(bot_id=bot_id, user_id=user_id, name=name)
                print("Creating new chat with name:", name)

                db.add(chat)
                db.commit()
                db.refresh(chat)

            new_message = Message(
                chat_id=chat.id, content=message, sender=MessageSender(sender)
            )

            db.add(new_message)
            db.commit()
            print("Stored message")

        except Exception as e:
            db.rollback()
            print("Error storing message", str(e))

        finally:
            db.close()
