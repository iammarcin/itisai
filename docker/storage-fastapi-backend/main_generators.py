from fastapi import FastAPI, HTTPException
from textGenerators.AITextGenerator import AITextGenerator
from textGenerators.ClaudeAITextGenerator import ClaudeTextGenerator
from speechRecognition.OpenAISpeechRecognition import OpenAISpeechRecognitionGenerator
from imageGenerators.OpenAIImageGenerator import OpenAIImageGenerator
from tts.OpenAITTS import OpenAITTSGenerator
from aws.awsProvider import awsProvider
from db.dbProvider import dbProvider
from garmin.garminProvider import garminProvider

import config as config
import logconfig

logger = logconfig.logger

# special function for garmin - to login on fastapi start
def initialize_garmin_provider():
    provider = garminProvider()
    login_successful = provider.login()
    if not login_successful:
        raise HTTPException(
            status_code=401, detail="Failed to authenticate with Garmin")
    return provider

# Define the helper classes as dependencies (suggested by chatgpt)
# it's better to use dependency injection to avoid tight coupling between the classes.
async def startup_event_generators(app: FastAPI):
    app.dependency_overrides[AITextGenerator] = get_text_generator
    app.dependency_overrides[OpenAISpeechRecognitionGenerator] = get_speech_generator

    # Initialize and login Garmin provider
    garmin_provider = initialize_garmin_provider()
    # Store the Garmin provider instance in the app state for later use
    app.state.garmin_provider = garmin_provider

def get_speech_generator():
    return OpenAISpeechRecognitionGenerator()

def get_tts_generator():
    return OpenAITTSGenerator()

def get_text_generator(model: str):
    if model == "claude-3-5-sonnet":
        return ClaudeTextGenerator()
    else:
        return AITextGenerator()

def get_image_generator():
    return OpenAIImageGenerator()

def get_s3_provider():
    return awsProvider()

def get_db_provider():
    return dbProvider()

def get_garmin_provider(app: FastAPI):
    return app.state.garmin_provider

# method used in multiple API endpoints - to simplify choosing generator
def get_generator(category: str, userSettings: dict):
    generators = {
        "text": {"function": get_text_generator},
        "image": {"function": get_image_generator},
        "speech": {"function": get_speech_generator},
        "tts": {"function": get_tts_generator},
        "provider.s3": {"function": get_s3_provider},
        "provider.db": {"function": get_db_provider},
    }

    if category in generators:
        if category == "text":
            model = userSettings.get("model")
            generator = generators[category]["function"](model)
        else:
            generator = generators[category]["function"]()
        return generator
    else:
        return None
