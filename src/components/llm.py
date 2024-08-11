from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.constants.prompts_dict import PROMPTS

load_dotenv()

store = {}
config = {"configurable": {"session_id": "abc1"}}

class LLM:
    def __init__(self):
        self.model = ChatGroq(model="llama3-8b-8192")      

    def get_session_history(self, session_id) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()

        return store[session_id]

    def chat(self, message, role) -> BaseMessage:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    PROMPTS[role],
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = prompt | self.model
        with_message_history = RunnableWithMessageHistory(chain, self.get_session_history)

        response = with_message_history.invoke(
            {"messages": [HumanMessage(content=message)]},
            config = config
        )
        # response = chain.invoke(
        #     # {"messages": [HumanMessage(content=message)]},
        #     config=config
        # )

        print(f"Store {store}")
        print(f"Config {config}")

        return response