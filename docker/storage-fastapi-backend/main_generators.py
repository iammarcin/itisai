from fastapi import FastAPI, HTTPException
from textGenerators.AITextGenerator import AITextGenerator
from speechRecognition.OpenAISpeechRecognition import OpenAISpeechRecognitionGenerator
from aws.awsProvider import awsProvider

import config as config

# Define the helper classes as dependencies (suggested by chatgpt)
# it's better to use dependency injection to avoid tight coupling between the classes.
async def startup_event_generators(app: FastAPI):
    app.dependency_overrides[AITextGenerator] = get_text_generator
    app.dependency_overrides[OpenAISpeechRecognitionGenerator] = get_speech_generator

def get_speech_generator():
    return OpenAISpeechRecognitionGenerator()

def get_text_generator():
    return AITextGenerator()

def get_s3_provider():
    return awsProvider()

# method used in multiple API endpoints - to simplify choosing generator
def get_generator(category: str, userSettings: dict):
    generators = {
        "text": {"function": get_text_generator},
        "speech": {"function": get_speech_generator},
        "provider.s3": {"function": get_s3_provider},
    }

    if category in generators:
        generator = generators[category]["function"]()
        return generator
    else:
        return None

