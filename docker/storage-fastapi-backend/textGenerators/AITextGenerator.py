from fastapi import HTTPException
from fastapi.responses import JSONResponse
from textGenerators.ChatHelpers import prepare_chat_history, prepare_message_content, truncate_image_urls_from_history, isItAnthropicModel
import json
from openai import OpenAI
from groq import Groq
import anthropic
from itisai_brain.text import getTextPromptTemplate

import config as config
import logconfig
logger = logconfig.logger


class AITextGenerator:
    def __init__(self):
        self.model_name = "gpt-4o-mini"
        # sometimes there are activities - that really just need cheap AI to process (for example setting session name)
        self.cheapest_model_name = "gpt-4o-mini"
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
        # how many user messages can be sent before we start trimming images or files attached (because later it doesn't make a lot of sense - because we switch topic etc)
        self.file_attached_message_limit = 3
        # OpenAI API works with URLs too, but Claude needs base64
        self.use_base64 = True
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
                elif user_settings["model"] == "GPT-4o-mini":
                    self.model_name = "gpt-4o-mini"
                    self.support_image_input = True
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
                elif user_settings["model"] == "Claude-3.5":
                    self.model_name = "claude-3-5-sonnet-20240620"
                    self.support_image_input = True
                    self.llm = anthropic.Anthropic()
                else:
                    self.model_name = self.cheapest_model_name
                    self.support_image_input = False
                    self.llm = OpenAI()

            self.set_system_prompt(
                user_settings["ai_character"] if "ai_character" in user_settings else "Assistant")

            if "temperature" in user_settings:
                self.temperature = user_settings["temperature"]

            if "memory_limit" in user_settings:
                self.memory_token_limit = user_settings["memory_limit"]

            if "streaming" in user_settings:
                self.streaming = user_settings["streaming"]

            if "file_attached_message_limit" in user_settings:
                self.file_attached_message_limit = user_settings["file_attached_message_limit"]

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
            elif action == "generate_session_name":
                self.model_name = self.cheapest_model_name
                self.llm = OpenAI()
                self.streaming = False
                self.temperature = 0.1
                return await self.generate_session_name(userInput, assetInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing Text request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing Text request")

    async def tools(self, action: str, userInput: dict, assetInput: dict, customerId: int = 1):
        if self.use_test_data:
            response = f"data: Test response from Text generator"
            return response

        chat_history = []
        chat_history.append({"role": "user", "content": userInput["prompt"]})

        logger.info("Using model: %s", self.model_name)

        if isItAnthropicModel(self.model_name):
            response = self.llm.messages.create(
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=chat_history,
                model=self.model_name
            )
            response_content = response.content

        else:
            response = self.llm.chat.completions.create(
                model=self.model_name,
                messages=chat_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False,
            )

            logger.debug("Response from Text generator: %s", response)

            response_content = response.choices[0].message.content
        return {'code': 200, 'success': True, 'message': {"status": "completed", "result": response_content}}

    def chat(self, userInput: dict, assetInput: dict, customerId: int = None):

        try:
            chat_history = userInput.get('chat_history') if userInput.get(
                'chat_history') is not None else []

            latest_user_message = userInput.get('prompt')

            # if it's more complex message - we need to process it (because there are differences between generator - especially if there are images)
            if isinstance(latest_user_message, list):
                latest_user_message = prepare_message_content(
                    latest_user_message, self.model_name, self.use_base64)
            # fail on purpose
            # test = userInput['test']
            # Trim messages to fit within the memory token limit
            chat_history = prepare_chat_history(chat_history, self.memory_token_limit, self.model_name, self.support_image_input,
                                                use_base64=self.use_base64, file_attached_message_limit=self.file_attached_message_limit)

            # Add system prompt and latest user message to chat history
            if not isItAnthropicModel(self.model_name):
                chat_history.append({"role": "system", "content": self.system_prompt})

            chat_history.append(latest_user_message)

            logger.info("Final chat history sent to API: %s", truncate_image_urls_from_history(chat_history))

            if self.use_test_data:
                # yield f"Hello"
                yield f"Test response from Text generator (streaming)"
                return

            logger.debug("Using model: %s", self.model_name)

            if isItAnthropicModel(self.model_name):
                if self.streaming:
                    with self.llm.messages.stream(
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
                    response = self.llm.messages.create(
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        system=self.system_prompt,
                        messages=chat_history,
                        model=self.model_name
                    )
                    print("RESPONSE: ", response)
                    # if no streaming - just throw whole response
                    yield f"{response.content}"
            else:
                response = self.llm.chat.completions.create(
                    model=self.model_name,
                    messages=chat_history,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
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

    async def generate_session_name(self, userInput: dict, assetInput: dict, customerId: int = 1):
        try:
            textToProcess = userInput.get('text')
            if textToProcess is None:
                raise HTTPException(
                    status_code=400, detail="Text to process is required")

            finalPrompt = """
Following is a message from chat application:
%s

Based on this message please generate a session name, that will represent accurately the topic of this conversation.
Please try to make session name as short as possible.
Respond with just single sentence consisting of session name. Don't add any other information.
            """ % (textToProcess)

            newUserInput = {"prompt": finalPrompt}
            response = await self.tools("generate_session_name", newUserInput, assetInput, customerId)

            finalAnswer = response["message"]["result"]
            # get rid of some characters
            finalAnswer = finalAnswer.replace('"', '')
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": finalAnswer}}, status_code=200)
        except Exception as e:
            logger.error("Error generating session name: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error generating session name")
