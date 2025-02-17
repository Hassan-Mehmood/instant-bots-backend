from fastapi import HTTPException

import aisuite as ai

from src.routers.utils import check_uuid
from src.db.database import SessionLocal
from src.models.models import Bot

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

    def chat(self, message:str, user_id:str, bot_id:str, model:str, chat_history: list):
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

            return response.choices[0].message.content

        except Exception as e:
            print("Exception in chat: ", str(e))
            raise HTTPException(status_code=500, detail="Error in chat")