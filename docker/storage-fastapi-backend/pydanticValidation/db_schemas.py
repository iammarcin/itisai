from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy import func, create_engine, DateTime, Column, Integer, String, Text, JSON, Boolean, TIMESTAMP, ForeignKey, CHAR, VARCHAR, text
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = 'ChatMessages'
    message_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey('ChatSessions.session_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    sender = Column(String(255), nullable=False)
    message = Column(Text)
    image_locations = Column(JSON)
    file_locations = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class ChatSession(Base):
    __tablename__ = 'ChatSessions'
    session_id = Column(String(36), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    session_name = Column(String(100))
    chat_history = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    last_update = Column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=func.now())

class ChatSessionResponse(BaseModel):
    session_id: str
    user_id: Optional[int]
    session_name: Optional[str]
    chat_history: Optional[Dict]
    created_at: Optional[str]
    last_update: Optional[str]