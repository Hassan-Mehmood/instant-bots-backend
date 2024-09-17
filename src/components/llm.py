from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.constants.prompts_dict import PROMPTS

from src.models.models import SessionLocal, Chat, Message

import uuid

load_dotenv()


class LLM:
    def __init__(self):
        self.model = ChatGroq(model="llama3-8b-8192")
        self.output_parser = StrOutputParser()
        self.user_id = None
        self.bot_id = None
        self.database = SessionLocal()
        self.config = {"configurable": {"session_id": ""}}
        self.store = {}

    def get_session_history(self, session_id) -> BaseChatMessageHistory:
        # Fetch chat history from the database based on session_id
        if session_id not in self.store:
            history = InMemoryChatMessageHistory()
            db_chats = self.database.query(Message).filter_by(chat_id=session_id).order_by(Message.created_at).all()
            for message in db_chats:
                if message.sender == "USER":
                    history.add_user_message(message.content)
                else:
                    history.add_ai_message(message.content)
            self.store[session_id] = history

        return self.store[session_id]

    def create_chat_if_not_exists(self, user_id, bot_id):
        print("Inside create_chat_if_not_exists function")
        chat = self.database.query(Chat).filter_by(user_id=user_id, bot_id=bot_id).first()
        print('CHAT Query result: ', chat)
        if chat is None:
            chat = Chat(
                id=str(uuid.uuid4()),
                user_id=user_id,
                bot_id=bot_id
            )

            print('CHAT Created: ', chat)

            self.database.add(chat)
            self.database.commit()

        print('CHAT ID: ', chat.id)
        return chat.id

    def chat(self, message, role, user_id, bot_id) -> BaseMessage:
        print("Chat function called")
        self.user_id = user_id
        self.bot_id = bot_id
        session_id = self.create_chat_if_not_exists(user_id, bot_id)

        self.config["configurable"]["session_id"] = session_id
        print('Config: ', self.config)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    PROMPTS[role],
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = prompt | self.model | self.output_parser
        with_message_history = RunnableWithMessageHistory(chain, self.get_session_history)

        response = with_message_history.invoke(
            {"messages": [HumanMessage(content=message)]},
            config = self.config
        )

        print('Model response arrived')

        new_message = self.store_message(message, session_id, "USER")
        new_response = self.store_message(response, session_id, "BOT")

        self.database.add(new_message)
        self.database.add(new_response)
        self.database.commit()

        return response

    def store_message(self, content, session_id, sender):
        print('Inside store_message function params', session_id, sender)

        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)

        message = Message(
            id = uuid.uuid4(),
            chat_id = session_id,
            sender = sender,
            content = content
        )

        return message