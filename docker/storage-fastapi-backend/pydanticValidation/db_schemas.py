from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy import func, create_engine, DateTime, Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, CHAR, VARCHAR, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import uuid

Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = 'ChatMessages'
    message_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey('ChatSessions.session_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    sender = Column(String(255), nullable=False)
    message = Column(Text)
    image_url = Column(Text)
    file_path = Column(Text)
    created_at = Column(DateTime, default=func.now())

class ChatSession(Base):
    __tablename__ = 'ChatSessions'
    session_id = Column(String(36), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    session_name = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    last_update = Column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=func.now())

class ChatSessionCreate(BaseModel):
    session_id: Optional[str] = None
    user_id: int
    session_name: Optional[str] = None