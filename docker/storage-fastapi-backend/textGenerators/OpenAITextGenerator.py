from fastapi.responses import StreamingResponse
from pydanticValidation.general_schemas import MediaModel
from openai import OpenAI
import traceback

#from helperUploadDownload import downloadContentFromURL


import logconfig, os, re
logger = logconfig.logger

# chat stream helpers
#from textGenerators.StreamHelpers import *
#from textGenerators.ChatHelpers import *

class OpenAITextGenerator:
  def __init__(self, openai_api_key):
    self.openai_api_key = openai_api_key
    #self.options = self.get_options()
    self.model_name = "gpt-3.5-turbo"
    #self.model_name = "gpt-4"
    #self.model_name = "ada"
    self.save_to_file = True
    self.save_to_file_iterator = 0
    self.streamingOn = False
    self.memory_token_limit = 1000
    self.prompt_total_limit = 2000
    # text generation timeout
    self.request_timeout = 180
    self.temperature = 0
    self.llm = OpenAI()

  def set_settings(self, userSettings={}):
    if userSettings:
        user_settings = userSettings.get("text", {})
        logger.debug("Setting user_settings: %s", user_settings)
        # Update model name
        if "model" in user_settings:
            self.model_name = user_settings["model"]

        # Update temperature
        if "temperature" in user_settings:
            self.temperature = user_settings["temperature"]

        # Update memory limit
        if "memory_limit" in user_settings:
            self.memory_token_limit = user_settings["memory_limit"]

  async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False, params: dict = {}):
    # OPTIONS
    self.set_settings(userSettings)

    logger.info(userSettings)
    streamEnabled = userSettings["stream"]

    try:
        response = self.llm.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
              {"role": "system", "content": "You are an expert!"},
              {"role": "user", "content": userInput["input"]}
            ],
            stream=streamEnabled,
        )
    except Exception as e:
        print("Error in creating campaigns from openAI:", str(e))
        return 503
    #return response["choices"][0]["message"]["content"]

    if streamEnabled:
      try:
        for chunk in response:
            current_content = chunk.choices[0].delta.content
            #current_content = chunk.choices[0].delta.get("content", "")
            #yield current_content
            #if chunk.choices[0].delta.content is not None:
            #    print(chunk.choices[0].delta.content, end="")
            #    logger.info(chunk.choices[0].delta.content)
      except Exception as e:
         logger.error("Openai stream error" + str(e))
         return 503
    else:
      logger.info("-"*100)
      logger.info(response)
      logger.info(response.choices)
      logger.info(response.choices[0])
      logger.info(response.choices[0].message.content)

      return response.choices[0].message.content

  def streamnow2(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False, params: dict = {}):
    # OPTIONS
    self.set_settings(userSettings)

    try:
        response = self.llm.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
              {"role": "system", "content": "You are an expert!"},
              {"role": "user", "content": userInput["input"]}
            ],
            stream=True,
        )
        logger.info("---"*100)
        for chunk in response:
            current_content = chunk.choices[0].delta.content
            #current_content = chunk.choices[0].delta.get("content", "")
            logger.info(current_content)
            if current_content is not None:
              yield current_content
            #if chunk.choices[0].delta.content is not None:
            #    print(chunk.choices[0].delta.content, end="")
            #    logger.info(chunk.choices[0].delta.content)
    except Exception as e:
        print("Error in creating campaigns from openAI:", str(e))

  def streamnow(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False, params: dict = {}):
    self.set_settings(userSettings)
    try:
        response = self.llm.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
              {"role": "system", "content": "You are an expert!"},
              {"role": "user", "content": userInput["input"]}
            ],
            stream=True,
        )
        for chunk in response:
            current_content = chunk.choices[0].delta.content
            if current_content is not None:
                logger.info(str(current_content))
                yield f"data: {current_content}\n\n"  # Format the output as a proper SSE message
    except Exception as e:
        print("Error in streaming from OpenAI:", str(e))
        yield "data: Error in streaming data.\n\n"  # Error message in SSE format


