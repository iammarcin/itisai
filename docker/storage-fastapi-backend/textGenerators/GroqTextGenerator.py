from fastapi.responses import StreamingResponse
from pydanticValidation.general_schemas import MediaModel
from openai import OpenAI
import traceback

import logconfig, os, re
logger = logconfig.logger

class GroqTextGenerator:
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

  async def job_status(self, job_id):
    return {'success': True, 'message': { "status": "completed" }, "code": 200 }

  async def process_job_request(self, api_input: dict):
    # PROCESS API INPUT
    action = api_input["action"]
    userInput = api_input["userInput"]
    assetInput = api_input["assetInput"] if "assetInput" in api_input else {}
    customerId = api_input["customerId"]
    userSettings = api_input["userSettings"]

    # OPTIONS
    self.set_settings(userSettings[api_input["category"]])

    if action == "generate" or action == "summary" or action == "rewrite":
      return { "success": False, "message": "Not ready", "code": 400 }
      #return await self.tools(action, userInput, assetInput, customerId, requestId, userSettings, returnTestData)
    elif action == "chat":
      return await self.chat(userInput, assetInput, customerId)
    elif action == "job_status":
      return await self.job_status(userInput)
    else:
      return { "success": False, "message": "Unknown action", "code": 400 }

  def chat(self, userInput: dict, assetInput: dict, customerId: int = None):
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


