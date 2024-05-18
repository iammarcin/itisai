from fastapi.responses import StreamingResponse
from pydanticValidation.general_schemas import MediaModel
from groq import Groq
from prompts.text import getTextPromptTemplate
import traceback

import logconfig, os, re
logger = logconfig.logger

class GroqTextGenerator:
  def __init__(self, openai_api_key):
    self.openai_api_key = openai_api_key
    #self.options = self.get_options()
    self.model_name = "llama3-8b-8192"
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
    self.llm = Groq( api_key=os.environ.get("GROQ_API_KEY") )


  def set_settings(self, user_settings={}):
    if user_settings:
        logger.debug("Setting user_settings: %s", user_settings)
        # Update model name
        if "model" in user_settings:
            if user_settings["model"] == "LLama 3 70b":
              self.model_name = "llama3-70b-8192"
            elif user_settings["model"] == "Mixtral 8x7b":
              self.model_name = "mixtral-8x7b-32768"
            elif user_settings["model"] == "Gemma 7b":
              self.model_name = "gemma-7b-it"
            else:
              self.model_name = "llama3-8b-8192"

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
    logger.info("template: %s" % template)
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
    logger.info("*"*100)
    logger.info(userInput)
    logger.info(userInput["prompt"])
    logger.info(self.system_prompt)
    logger.info(self.streaming)
    try:
        if self.use_test_data:
          yield f"data: Test response from Groq"
          return

        response = self.llm.chat.completions.create(
            model=self.model_name,
            messages=[
              {"role": "system", "content": self.system_prompt},
              {"role": "user", "content": userInput["prompt"]}
            ],
            temperature=self.temperature,
            stream=self.streaming,
        )

        if self.streaming:
          for chunk in response:
              current_content = chunk.choices[0].delta.content
              if current_content is not None:
                  logger.info(str(current_content))

                  yield f"data: {current_content}\n\n"  # Format the output as a proper SSE message
        else:
          # if no streaming - just throw whole response
          yield f"data: {response.choices[0].message.content}"
    except Exception as e:
        logger.error("Error in streaming from Groq:", str(e))
        yield "data: Error in streaming data.\n\n"  # Error message in SSE format



