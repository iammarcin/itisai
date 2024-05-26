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
    customer_id = Column(Integer, ForeignKey('Users.customer_id'), nullable=False)
    sender = Column(String(255), nullable=False)
    message = Column(Text)
    image_locations = Column(JSON)
    file_locations = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class ChatSession(Base):
    __tablename__ = 'ChatSessions'
    session_id = Column(String(36), primary_key=True, index=True, default=uuid.uuid4)
    customer_id = Column(Integer, ForeignKey('Users.customer_id'))
    session_name = Column(String(100))
    ai_character_name = Column(String(50))
    chat_history = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    last_update = Column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = 'Users'
    customer_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=func.now())


