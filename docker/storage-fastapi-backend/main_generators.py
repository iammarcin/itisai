from fastapi import FastAPI, HTTPException
from textGenerators.OpenAITextGenerator import OpenAITextGenerator
from textGenerators.GroqTextGenerator import GroqTextGenerator
#from speechGenerators.OpenAISpeechGenerator import OpenAISpeechGenerator

import config as config

# Define the helper classes as dependencies (suggested by chatgpt)
# it's better to use dependency injection to avoid tight coupling between the classes.
async def startup_event_generators(app: FastAPI):
    app.dependency_overrides[OpenAITextGenerator] = get_text_generator
    #app.dependency_overrides[OpenAISpeechGenerator] = get_speech_generator

'''
def get_speech_generator(speechGenerator: str):
    if speechGenerator == "openai":
        return OpenAISpeechGenerator(
            config.defaults['openai_api_key'] # not really needed - as taken from env
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid speech generator")
'''
def get_text_generator(userSettings: dict):

    user_model = userSettings.get("model")
    # if starts with GPT, then it's OpenAI
    if user_model and user_model.startswith("GPT"):
        user_text_generator = "openai"
    elif user_model and user_model.startswith("LLama"):
        user_text_generator = "groq"
    else:
        user_text_generator = None

    if user_text_generator == "openai":
        return OpenAITextGenerator(
            config.defaults['openai_api_key']
        )
    elif user_text_generator == "groq":
        return GroqTextGenerator(
            config.defaults['groq_api_key']
        )
    else:
        raise None

# method used in multiple API endpoints - to simplify choosing generator
def get_generator(category: str, userSettings: dict):
    generators = {
        "text": {"function": get_text_generator},
        #"speech": {"function": get_speech_generator},
    }

    if category in generators:
        generator = generators[category]["function"](userSettings)
        return generator
    else:
        return None

