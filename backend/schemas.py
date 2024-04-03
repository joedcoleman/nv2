from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    content: List
    role: str
    status: Optional[str] = None
    conversation_id: str
    meta_data: Optional[dict] = {}


class MessageIn(MessageBase):
    pass


class MessageOut(MessageBase):
    created_at: datetime


class ConversationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageBase] = []
    meta_data: Optional[dict] = {}


class ConversationIn(ConversationBase):
    pass


class ConversationOut(ConversationBase):
    pass


class Settings(BaseModel):
    models: List[str]
