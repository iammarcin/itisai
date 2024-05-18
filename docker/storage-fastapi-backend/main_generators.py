from fastapi import FastAPI, HTTPException
from textGenerators.AITextGenerator import AITextGenerator

#from speechGenerators.OpenAISpeechGenerator import OpenAISpeechGenerator

import config as config

# Define the helper classes as dependencies (suggested by chatgpt)
# it's better to use dependency injection to avoid tight coupling between the classes.
async def startup_event_generators(app: FastAPI):
    app.dependency_overrides[AITextGenerator] = get_text_generator
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
def get_text_generator():
    return AITextGenerator()

# method used in multiple API endpoints - to simplify choosing generator
def get_generator(category: str, userSettings: dict):
    generators = {
        "text": {"function": get_text_generator},
        #"speech": {"function": get_speech_generator},
    }

    if category in generators:
        generator = generators[category]["function"]()
        return generator
    else:
        return None

