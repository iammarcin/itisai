from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from pydanticValidation.general_schemas import MediaModel
from textGenerators.ChatHelpers import prepare_chat_history
import anthropic
import traceback
from itisai_brain.text import getTextPromptTemplate

import config as config
import logconfig
import os
import re
logger = logconfig.logger


class ClaudeTextGenerator:
    def __init__(self):
        self.model_name = "claude-3-5-sonnet-20240620"
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
        self.max_tokens = 3072
        self.system_prompt = "You are an expert!"
        self.use_test_data = False
        self.client = anthropic.Anthropic()

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
                    # self.model_name = "gpt-3.5-turbo"
                    self.support_image_input = False
                else:
                    # if not specified, use GPT-3.5
                    # self.model_name = "gpt-3.5-turbo"
                    self.support_image_input = False

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
        # add ai_character text at the end
        self.system_prompt = self.system_prompt + " " + ai_character + ":"

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)

        try:
            if action == "chat":
                return self.chat(userInput, assetInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing Text request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing Text request")

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

            chat_history.append(
                {"role": "user", "content": latest_user_message})

            logger.debug("Chat history: %s", chat_history)

            if self.use_test_data:
                yield f"Test response from Text generator (streaming)"
                return

            print("STREAMING: ", self.streaming)

            if self.streaming:
                with self.client.messages.stream(
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.system_prompt,
                    messages=chat_history,
                    model=self.model_name
                ) as stream:
                    for text in stream.text_stream:
                        print(text, end="", flush=True)
                        yield f"{text}"
            else:
                response = self.client.messages.create(
                    model=self.model_name,
                    system=self.system_prompt,
                    messages=chat_history,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    # temperature=self.temperature,
                    # stream=self.streaming,
                )
                print("RESPONSE: ", response)
                # if no streaming - just throw whole response
                yield f"{response.content}"
        except Exception as e:
            logger.error("Error in streaming from Text generator:", str(e))
            # Error message in SSE format
            yield config.defaults['ERROR_MESSAGE_FOR_TEXT_GEN']
