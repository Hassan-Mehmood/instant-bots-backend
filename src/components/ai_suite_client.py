from fastapi import HTTPException, BackgroundTasks

import aisuite as ai

from src.db.database import SessionLocal
from src.models.models import Bot, Chat, Message

from src.routers.utils import check_uuid
from src.models.utils import MessageSender

import os
from dotenv import load_dotenv

load_dotenv()

class AiSuiteClient:
    def __init__(self):
        self.db = SessionLocal()
        self.client = ai.Client()
        self.load_keys()
    
    def load_keys(self):
        os.getenv("OPENAI_API_KEY")
        os.getenv("ANTHROPIC_API_KEY")
        os.getenv("GROQ_API_KEY")

    def chat(self, message:str, user_id:str, bot_id:str, model:str, chat_history: list, background_tasks: BackgroundTasks):
        try:
            if not message or not model:
                raise HTTPException(status_code=400, detail="Please provide model and message")

            if not check_uuid(user_id) or not check_uuid(bot_id):
                raise HTTPException(status_code=400, detail="Please provide valid user id and bot id")

            bot = self.db.query(Bot).filter_by(id=bot_id, user_id=user_id).first()

            if not bot:
                raise HTTPException(status_code=404, detail="Bot not found")
            
            prompt = bot.prompt

            chat_history.insert(0, {"role": "system", "content": prompt})
            chat_history.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(model=model, messages=chat_history)

            background_tasks.add_task(self.store_message, bot_id, user_id, message, "USER")
            background_tasks.add_task(self.store_message, bot_id, user_id, response.choices[0].message.content, "BOT")

            return {
                "role": "assistant",
                "content": response.choices[0].message.content
            }

        except Exception as e:
            print("Exception in chat: ", str(e))
            raise HTTPException(status_code=500, detail="Error in chat")

    def store_message(self, bot_id, user_id, message, sender):
        try:
            chat = self.db.query(Chat).filter_by(bot_id=bot_id, user_id=user_id).first()       

            if not chat:
                print("Chat not found, creating a new one")
                new_chat = Chat(
                    bot_id=bot_id,
                    user_id=user_id
                )

                self.db.add(new_chat)
                self.db.commit()

                print("Chat created")
                chat = new_chat

            new_message = Message(
                chat_id=chat.id,
                content=message,
                sender=MessageSender(sender)
            )

            self.db.add(new_message)
            self.db.commit()

        except Exception as e:
            print('Exception in store_message: ', e)
            raise HTTPException(status_code=500, detail="Error in storing message")