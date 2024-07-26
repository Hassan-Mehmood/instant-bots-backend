import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage


load_dotenv()

class LLM:
    def __init__(self):
        self.model = ChatGroq(model="llama3-8b-8192")


    def chat(self, message):
        response = self.model.invoke([HumanMessage(content=message)])

        return response