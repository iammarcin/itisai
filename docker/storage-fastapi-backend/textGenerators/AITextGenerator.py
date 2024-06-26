from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from pydanticValidation.general_schemas import MediaModel
from textGenerators.ChatHelpers import prepare_chat_history
from openai import OpenAI
from groq import Groq
import traceback
from itisai_brain.text import getTextPromptTemplate

import config as config
import logconfig
import os
import re
logger = logconfig.logger


class AITextGenerator:
    def __init__(self):
        self.model_name = "gpt-3.5-turbo"
        self.save_to_file = True
        self.save_to_file_iterator = 0
        self.streaming = False
        # some model support images as input, some not
        self.support_image_input = False
        self.memory_token_limit = 1000
        self.prompt_total_limit = 2000
        # text generation timeout - can it be set?!
        self.request_timeout = 180
        self.temperature = 0
        self.system_prompt = "You are an expert!"
        self.use_test_data = False
        self.llm = OpenAI()

    def set_settings(self, user_settings={}):
        if user_settings:
            # if we want to return test data
            self.use_test_data = user_settings["general"]["returnTestData"]

            # and now process text settings
            user_settings = user_settings.get("text", {})
            logger.debug("Setting user_settings: %s", user_settings)
            # Update model name
            if "model" in user_settings:
                if user_settings["model"] == "GPT-3.5":
                    self.model_name = "gpt-3.5-turbo"
                    self.support_image_input = False
                    self.llm = OpenAI()
                elif user_settings["model"] == "GPT-4":
                    self.model_name = "gpt-4-turbo"
                    self.support_image_input = True
                    self.llm = OpenAI()
                elif user_settings["model"] == "GPT-4o":
                    self.model_name = "gpt-4o"
                    self.support_image_input = True
                    self.llm = OpenAI()
                elif user_settings["model"] == "LLama 3 70b":
                    self.model_name = "llama3-70b-8192"
                    self.support_image_input = False
                    self.llm = Groq()
                elif user_settings["model"] == "LLama 3 8b":
                    self.model_name = "llama3-8b-8192"
                    self.support_image_input = False
                    self.llm = Groq()
                elif user_settings["model"] == "Mixtral 8x7b":
                    self.model_name = "mixtral-8x7b-32768"
                    self.support_image_input = False
                    self.llm = Groq()
                elif user_settings["model"] == "Gemma 7b":
                    self.model_name = "gemma-7b-it"
                    self.support_image_input = False
                    self.llm = Groq()
                else:
                    # if not specified, use GPT-3.5
                    self.model_name = "gpt-3.5-turbo"
                    self.support_image_input = False
                    self.llm = OpenAI()

            # Set system prompt
            self.set_system_prompt(
                user_settings["ai_character"] if "ai_character" in user_settings else "Assistant")

            # Update temperature
            if "temperature" in user_settings:
                self.temperature = user_settings["temperature"]

            # Update memory limit
            if "memory_limit" in user_settings:
                self.memory_token_limit = user_settings["memory_limit"]

            if "streaming" in user_settings:
                self.streaming = user_settings["streaming"]

    def set_system_prompt(self, ai_character: str):
        template = getTextPromptTemplate(ai_character)['template']
        self.system_prompt = template

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)

        try:
            if action == "generate" or action == "summary" or action == "rewrite":
                return await self.tools(action, userInput, assetInput, customerId)
            elif action == "chat":
                return self.chat(userInput, assetInput, customerId)
            elif action == "job_status":
                return self.job_status(userInput)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing Text request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing Text request")

    async def tools(self, action: str, userInput: dict, assetInput: dict, customerId: int = None):
        if self.use_test_data:
            response = f"data: Test response from Text generator"
            return response

        chat_history = []
        chat_history.append({"role": "user", "content": userInput["prompt"]})

        response = self.llm.chat.completions.create(
            model=self.model_name,
            messages=chat_history,
            temperature=self.temperature,
            stream=False,
        )

        logger.info("Response from Text generator: %s", response)

        response_content = response.choices[0].message.content
        return {'code': 200, 'success': True, 'message': {"status": "completed", "result": response_content}}

    def chat(self, userInput: dict, assetInput: dict, customerId: int = None):

        try:
            chat_history = userInput.get('chat_history') if userInput.get(
                'chat_history') is not None else []
            latest_user_message = userInput.get('prompt')
            # fail on purpose
            # test = userInput['test']
            # Trim messages to fit within the memory token limit
            chat_history = prepare_chat_history(
                chat_history, self.memory_token_limit, self.model_name, self.support_image_input)

            # Add system prompt and latest user message to chat history
            chat_history.append(
                {"role": "system", "content": self.system_prompt})
            chat_history.append(
                {"role": "user", "content": latest_user_message})

            logger.debug("Chat history: %s", chat_history)

            if self.use_test_data:
                yield f"Test response from Text generator (streaming)"
                return

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
                        # logger.debug(str(current_content))

                        # Format the output as a proper SSE message
                        yield f"{current_content}"
            else:
                # if no streaming - just throw whole response
                yield f"{response.choices[0].message.content}"
        except Exception as e:
            logger.error("Error in streaming from Text generator:", str(e))
            # Error message in SSE format
            yield config.defaults['ERROR_MESSAGE_FOR_TEXT_GEN']
