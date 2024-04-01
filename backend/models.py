import uuid
from datetime import datetime
import pytz
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    title = Column(String, nullable=True)
    created_at = Column(
        String,
        default=lambda: datetime.now(pytz.timezone("America/Denver")).isoformat(),
    )
    updated_at = Column(
        String,
        onupdate=lambda: datetime.now(pytz.timezone("America/Denver")).isoformat(),
    )
    meta_data = Column(JSON, nullable=True)
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    content = Column(JSON)
    role = Column(String)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
