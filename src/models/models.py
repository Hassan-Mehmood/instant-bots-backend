from sqlalchemy import create_engine, Column, Integer, String, UUID, DateTime, func, ForeignKey, Enum
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship
import os

from src.models.utils import TransactionType, MessageSender

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    credits = Column(Integer)
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)

class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    user: Mapped['User'] = relationship("User", back_populates="transactions")
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Integer)
    bot_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bots.id'))
    bot: Mapped['Bot'] = relationship("Bot", back_populates="transactions")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)

class Bot(Base):
    __tablename__ = 'bots'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    prompt = Column(String) 
    price = Column(Integer)
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="bot")
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="bot")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)

class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    user: Mapped['User'] = relationship("User", back_populates="chats")
    bot_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bots.id'))
    bot: Mapped['Bot'] = relationship("Bot", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now) 

class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    chat_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('chats.id'))
    chat: Mapped['Chat'] = relationship("Chat", back_populates="messages")
    content = Column(String) 
    sender = Column(Enum(MessageSender), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now) 