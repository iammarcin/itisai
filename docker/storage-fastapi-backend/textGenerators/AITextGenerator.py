from fastapi.responses import StreamingResponse
from pydanticValidation.general_schemas import MediaModel
from openai import OpenAI
from groq import Groq
import traceback
from prompts.text import getTextPromptTemplate
#from helperUploadDownload import downloadContentFromURL


import logconfig, os, re
logger = logconfig.logger

# chat stream helpers
#from textGenerators.StreamHelpers import *
#from textGenerators.ChatHelpers import *

class AITextGenerator:
  def __init__(self):
    self.model_name = "gpt-3.5-turbo"
    self.save_to_file = True
    self.save_to_file_iterator = 0
    self.streaming = False
    self.memory_token_limit = 1000
    self.prompt_total_limit = 2000
    # text generation timeout
    self.request_timeout = 180
    self.temperature = 0
    self.system_prompt = "You are an expert!"
    self.use_test_data = False
    self.llm = OpenAI()

  def set_settings(self, user_settings={}):
    if user_settings:
        logger.debug("Setting user_settings: %s", user_settings)
        # Update model name
        if "model" in user_settings:
            if user_settings["model"] == "GPT-3.5":
              self.model_name = "gpt-3.5-turbo"
              self.llm = OpenAI()
            elif user_settings["model"] == "GPT-4":
              self.model_name = "gpt-4-turbo"
              self.llm = OpenAI()
            elif user_settings["model"] == "GPT-4o":
              self.model_name = "gpt-4o"
              self.llm = OpenAI()
            elif user_settings["model"] == "LLama 3 70b":
              self.model_name = "llama3-70b-8192"
              self.llm = Groq()
            elif user_settings["model"] == "LLama 3 8b":
              self.model_name = "llama3-8b-8192"
              self.llm = Groq()
            elif user_settings["model"] == "Mixtral 8x7b":
              self.model_name = "mixtral-8x7b-32768"
              self.llm = Groq()
            elif user_settings["model"] == "Gemma 7b":
              self.model_name = "gemma-7b-it"
              self.llm = Groq()
            else:
              # if not specified, use GPT-3.5
              self.model_name = "gpt-3.5-turbo"
              self.llm = OpenAI()

        # Set system prompt
        self.set_system_prompt(user_settings["ai_character"] if "ai_character" in user_settings else "Assistant")

        # Update temperature
        if "temperature" in user_settings:
            self.temperature = user_settings["temperature"]

        # Update memory limit
        if "memory_limit" in user_settings:
            self.memory_token_limit = user_settings["memory_limit"]

        if "streaming" in user_settings:
            self.streaming = user_settings["streaming"]

  async def job_status(self, job_id):
    return {'success': True, 'message': { "status": "completed" }, "code": 200 }

  def set_system_prompt(self, ai_character: str):

    template = getTextPromptTemplate("brainstorm%s" % ai_character)['template']
    self.system_prompt = template

  def process_job_request(self, api_input: dict):
    logger.info("--"*20)
    logger.info(api_input)
    # PROCESS API INPUT
    action = api_input.action
    userInput = api_input.userInput
    # if set
    assetInput = api_input.assetInput if "assetInput" in api_input else {}
    customerId = api_input.customerId
    userSettings = api_input.userSettings

    # OPTIONS
    self.set_settings(userSettings[api_input.category])

    # if we want to return test data
    self.use_test_data = userSettings["general"]["returnTestData"]

    if action == "generate" or action == "summary" or action == "rewrite":
      return { "success": False, "message": "Not ready", "code": 400 }
      #return await self.tools(action, userInput, assetInput, customerId, requestId, userSettings, returnTestData)
    elif action == "chat":
      return self.chat(userInput, assetInput, customerId)
    elif action == "job_status":
      return self.job_status(userInput)
    else:
      return { "success": False, "message": "Unknown action", "code": 400 }

  def chat(self, userInput: dict, assetInput: dict, customerId: int = None):

    try:
        if self.use_test_data:
          yield f"data: Test response from Text generator"
          return

        chat_history = userInput.get('chat_history') if userInput.get('chat_history') != None else []

        chat_history.append({"role": "system", "content": self.system_prompt})
        chat_history.append({"role": "user", "content": userInput["prompt"]})

        logger.info(chat_history)

        response = self.llm.chat.completions.create(
            model=self.model_name,
            messages=chat_history,
            temperature=self.temperature,
            stream=self.streaming,
        )

        if self.streaming:
          for chunk in response:
              current_content = chunk.choices[0].delta.content
              if current_content is not None:
                  logger.debug(str(current_content))

                  yield f"data: {current_content}\n\n"  # Format the output as a proper SSE message
        else:
          # if no streaming - just throw whole response
          yield f"data: {response.choices[0].message.content}"
    except Exception as e:
        logger.error("Error in streaming from Text generator:", str(e))
        yield "data: Error in streaming data.\n\n"  # Error message in SSE format


