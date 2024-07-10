from sqlalchemy import Column, Integer, Float, String, DateTime
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


#### GARMIN #######
# SLEEP
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

# USER SUMMARY
class UserSummary(Base):
    __tablename__ = 'get_user_summary'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    total_kilocalories = Column(Float, nullable=True)
    active_kilocalories = Column(Float, nullable=True)
    bmr_kilocalories = Column(Float, nullable=True)
    total_steps = Column(Integer, nullable=True)
    total_distance_meters = Column(Integer, nullable=True)
    min_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    resting_heart_rate = Column(Integer, nullable=True)
    last_seven_days_avg_resting_heart_rate = Column(Integer, nullable=True)
    vigorous_intensity_minutes = Column(Integer, nullable=True)
    moderate_intensity_minutes = Column(Integer, nullable=True)
    rest_stress_duration = Column(Integer, nullable=True)
    low_stress_duration = Column(Integer, nullable=True)
    activity_stress_duration = Column(Integer, nullable=True)
    medium_stress_duration = Column(Integer, nullable=True)
    high_stress_duration = Column(Integer, nullable=True)
    stress_qualifier = Column(String(50), nullable=True)
    body_battery_charged_value = Column(Integer, nullable=True)
    body_battery_drained_value = Column(Integer, nullable=True)
    body_battery_highest_value = Column(Integer, nullable=True)
    body_battery_lowest_value = Column(Integer, nullable=True)
    body_battery_most_recent_value = Column(Integer, nullable=True)
    avg_waking_respiration_value = Column(Float, nullable=True)
    highest_respiration_value = Column(Float, nullable=True)
    lowest_respiration_value = Column(Float, nullable=True)
    latest_respiration_value = Column(Float, nullable=True)

class BodyComposition(Base):
    __tablename__ = 'get_body_composition'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    weight = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    body_fat_mass = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    body_water_mass = Column(Float, nullable=True)
    body_water_percentage = Column(Float, nullable=True)
    bone_mass = Column(Float, nullable=True)
    bone_mass_percentage = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    muscle_mass_percentage = Column(Float, nullable=True)
    visceral_fat = Column(Float, nullable=True)
    basal_metabolic_rate = Column(Integer, nullable=True)

class HRVData(Base):
    __tablename__ = 'get_hrv_data'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    weekly_avg = Column(Integer, nullable=True)
    last_night_avg = Column(Integer, nullable=True)
    status = Column(String(50), nullable=True)
    baseline_balanced_low = Column(Integer, nullable=True)
    baseline_balanced_upper = Column(Integer, nullable=True)

class TrainingReadiness(Base):
    __tablename__ = 'get_training_readiness'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    level = Column(String(50), nullable=True)
    score = Column(Integer, nullable=True)
    sleep_score = Column(Integer, nullable=True)
    sleep_score_factor_feedback = Column(String(255), nullable=True)
    recovery_time_factor_feedback = Column(String(255), nullable=True)
    recovery_time = Column(Integer, nullable=True)
    acute_load = Column(Integer, nullable=True)
    hrv_weekly_average = Column(Integer, nullable=True)
    hrv_factor_feedback = Column(String(255), nullable=True)
    stress_history_factor_feedback = Column(String(255), nullable=True)
    sleep_history_factor_feedback = Column(String(255), nullable=True)

class EnduranceScore(Base):
    __tablename__ = 'get_endurance_score'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    overall_score = Column(Integer, nullable=True)
    classification = Column(Integer, nullable=True)
    classification_lower_limit_intermediate = Column(Integer, nullable=True)
    classification_lower_limit_trained = Column(Integer, nullable=True)
    classification_lower_limit_well_trained = Column(Integer, nullable=True)
    classification_lower_limit_expert = Column(Integer, nullable=True)
    classification_lower_limit_superior = Column(Integer, nullable=True)
    classification_lower_limit_elite = Column(Integer, nullable=True)
    contributors = Column(JSON, nullable=True)

class TrainingStatus(Base):
    __tablename__ = 'get_training_status'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    daily_training_load_acute = Column(Integer, nullable=True)
    daily_training_load_acute_feedback = Column(String(50), nullable=True)
    daily_training_load_chronic = Column(Float, nullable=True)
    min_training_load_chronic = Column(Float, nullable=True)
    max_training_load_chronic = Column(Float, nullable=True)
    vo2_max_precise_value = Column(Float, nullable=True)
    vo2_max_feedback = Column(String(50), nullable=True)
    monthly_load_anaerobic = Column(Float, nullable=True)
    monthly_load_aerobic_high = Column(Float, nullable=True)
    monthly_load_aerobic_low = Column(Float, nullable=True)
    monthly_load_aerobic_low_target_min = Column(Float, nullable=True)
    monthly_load_aerobic_low_target_max = Column(Float, nullable=True)
    monthly_load_aerobic_high_target_min = Column(Float, nullable=True)
    monthly_load_aerobic_high_target_max = Column(Float, nullable=True)
    monthly_load_anaerobic_target_min = Column(Float, nullable=True)
    monthly_load_anaerobic_target_max = Column(Float, nullable=True)
    training_balance_feedback_phrase = Column(String(50), nullable=True)

class FitnessAge(Base):
    __tablename__ = 'get_fitness_age'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    chronological_age = Column(Integer, nullable=True)
    fitness_age = Column(Float, nullable=True)
    body_fat_value = Column(Float, nullable=True)
    vigorous_days_avg_value = Column(Float, nullable=True)
    rhr_value = Column(Integer, nullable=True)
    vigorous_minutes_avg_value = Column(Float, nullable=True)

class TrainingData(Base):
    __tablename__ = 'get_activities'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, index=True)
    calendar_date = Column(DateTime, index=True)
    activity_id = Column(Integer, nullable=False, unique=True)
    activity_type = Column(String(50), nullable=True)
    activity_name = Column(String(150), nullable=True)
    description = Column(String(255), nullable=True)
    distance = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    elevation_gain = Column(Float, nullable=True)
    elevation_loss = Column(Float, nullable=True)
    min_elevation = Column(Float, nullable=True)
    max_elevation = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)
    bmr_calories = Column(Float, nullable=True)
    steps = Column(Integer, nullable=True)
    aerobic_training_effect = Column(Float, nullable=True)
    anaerobic_training_effect = Column(Float, nullable=True)
    activity_training_load = Column(Float, nullable=True)
    training_effect_label = Column(String(50), nullable=True)
    aerobic_training_effect_message = Column(String(255), nullable=True)
    anaerobic_training_effect_message = Column(String(255), nullable=True)
    moderate_intensity_minutes = Column(Integer, nullable=True)
    vigorous_intensity_minutes = Column(Integer, nullable=True)
    difference_body_battery = Column(Integer, nullable=True)
    secs_in_zone1 = Column(Float, nullable=True)
    secs_in_zone2 = Column(Float, nullable=True)
    secs_in_zone3 = Column(Float, nullable=True)
    secs_in_zone4 = Column(Float, nullable=True)
    secs_in_zone5 = Column(Float, nullable=True)
