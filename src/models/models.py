from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    UUID,
    DateTime,
    func,
    ForeignKey,
    Enum,
    Table,
)
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship
import os
import uuid

from src.models.utils import TransactionType, MessageSender, BotVisibility

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


#! ------------------- Secondary Tables ------------------------------

users_bots = Table(
    "users_bots",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id"), primary_key=True),
    Column("bot_id", UUID, ForeignKey("bots.id"), primary_key=True),
)


#! ------------------- Primary Tables -------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    credits = Column(Integer)

    # One-to-Many Relationship: A user can have multiple private bots
    bots: Mapped[list["Bot"]] = relationship(
        "Bot", back_populates="user", cascade="all, delete-orphan"
    )
    favorite_bots: Mapped[list["Bot"]] = relationship(
        "Bot", secondary="users_bots", back_populates="favorite_users"
    )

    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user"
    )

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)


class Bot(Base):
    __tablename__ = "bots"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name = Column(String)
    description = Column(String)
    prompt = Column(String)
    avatar = Column(String)

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="bots", foreign_keys=[user_id]
    )
    favorite_users: Mapped[list["User"]] = relationship(
        "User", secondary="users_bots", back_populates="favorite_bots"
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="bot"
    )
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="bot")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Integer)
    bot_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bots.id"))
    bot: Mapped["Bot"] = relationship("Bot", back_populates="transactions")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="chats")
    bot_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bots.id"))
    bot: Mapped["Bot"] = relationship("Bot", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    chat_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chats.id"))
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    content = Column(String)
    sender = Column(Enum(MessageSender), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
