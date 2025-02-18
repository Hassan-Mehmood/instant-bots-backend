from sqlalchemy import Enum
from enum import Enum as PyEnum

class TransactionType(PyEnum):
    PURCHASE = "PURCHASE"
    SPEND = "SPEND"

class MessageSender(PyEnum):
    USER = "USER"
    BOT = "BOT"

class BotVisibility(str, PyEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"