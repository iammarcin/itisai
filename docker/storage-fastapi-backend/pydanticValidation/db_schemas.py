from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy import func, create_engine, DateTime, Column, Integer, String, Text, JSON, Float, Boolean, TIMESTAMP, ForeignKey, CHAR, VARCHAR, text
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = 'ChatMessages'
    message_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey(
        'ChatSessions.session_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey(
        'Users.customer_id'), nullable=False)
    sender = Column(String(255), nullable=False)
    message = Column(Text)
    image_locations = Column(JSON)
    file_locations = Column(JSON)
    created_at = Column(DateTime, default=func.now())


class ChatSession(Base):
    __tablename__ = 'ChatSessions'
    session_id = Column(String(36), primary_key=True,
                        index=True, default=uuid.uuid4)
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
    password = Column(String(100), nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=func.now())


class SleepData(Base):
    __tablename__ = 'get_sleep_data'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    sleep_time_seconds = Column(Integer, nullable=True)
    nap_time_seconds = Column(Integer, nullable=True)
    deep_sleep_seconds = Column(Integer, nullable=True)
    light_sleep_seconds = Column(Integer, nullable=True)
    rem_sleep_seconds = Column(Integer, nullable=True)
    awake_sleep_seconds = Column(Integer, nullable=True)
    average_respiration_value = Column(Float, nullable=True)
    lowest_respiration_value = Column(Float, nullable=True)
    highest_respiration_value = Column(Float, nullable=True)
    awake_count = Column(Integer, nullable=True)
    avg_sleep_stress = Column(Float, nullable=True)
    sleep_score_feedback = Column(String(255), nullable=True)
    sleep_score_insight = Column(String(255), nullable=True)
    sleep_score_personalized_insight = Column(String(255), nullable=True)
    overall_score_value = Column(Integer, nullable=True)
    overall_score_qualifier = Column(String(50), nullable=True)
    rem_percentage_value = Column(Integer, nullable=True)
    rem_percentage_qualifier = Column(String(50), nullable=True)
    rem_optimal_start = Column(Float, nullable=True)
    rem_optimal_end = Column(Float, nullable=True)
    restlessness_qualifier = Column(String(50), nullable=True)
    restlessness_optimal_start = Column(Float, nullable=True)
    restlessness_optimal_end = Column(Float, nullable=True)
    light_percentage_value = Column(Integer, nullable=True)
    light_percentage_qualifier = Column(String(50), nullable=True)
    light_optimal_start = Column(Float, nullable=True)
    light_optimal_end = Column(Float, nullable=True)
    deep_percentage_value = Column(Integer, nullable=True)
    deep_percentage_qualifier = Column(String(50), nullable=True)
    deep_optimal_start = Column(Float, nullable=True)
    deep_optimal_end = Column(Float, nullable=True)
    avg_overnight_hrv = Column(Float, nullable=True)
    resting_heart_rate = Column(Integer, nullable=True)
    body_battery_change = Column(Integer, nullable=True)
    restless_moments_count = Column(Integer, nullable=True)
