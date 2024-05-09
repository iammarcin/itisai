from fastapi.responses import StreamingResponse

from langchain.chat_models import ChatOpenAI
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate

from langchain.memory import ConversationTokenBufferMemory
from langchain.schema import HumanMessage, messages_from_dict
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import AsyncCallbackManager
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import NLTKTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain import LLMChain
from pydanticValidation.general_schemas import MediaModel
import traceback

from helperUploadDownload import downloadContentFromURL


import logconfig, os, re
logger = logconfig.logger

# chat stream helpers
from textGenerators.StreamHelpers import *
from textGenerators.ChatHelpers import *

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
    self.callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    self.llm = ChatOpenAI(model_name=self.model_name, streaming=self.streamingOn, request_timeout=self.request_timeout, callback_manager=self.callback_manager, verbose=True, temperature=self.temperature)
    self.memory = ConversationTokenBufferMemory(llm=self.llm, max_token_limit=self.memory_token_limit)
    # this is used in summary - so too long docs wont be processed (maybe for myself i can do it longer)
    self.MAX_LIMIT_TEXT_FOR_SUMMARY = 1000

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

        self.llm = ChatOpenAI(model_name=self.model_name, streaming=self.streamingOn, request_timeout=self.request_timeout, callback_manager=self.callback_manager, verbose=True, temperature=self.temperature)


  # getter and setter for save_to_file variable
  def get_save_to_file(self):
    return self.save_to_file

  def set_save_to_file(self, save_to_file):
    self.save_to_file = save_to_file

  # getter and setter for save_to_file_iterator variable
  def get_save_to_file_iterator(self):
    return self.save_to_file_iterator

  def set_save_to_file_iterator(self, save_to_file_iterator):
    self.save_to_file_iterator = save_to_file_iterator

  def save2file(self, content, customerId, requestId):
    self.save_to_file_iterator += 1
    filename = f"output_{self.save_to_file_iterator}.txt"
    filename = f"/storage/testApi/{customerId}/{requestId}/{filename}"

    try:
      if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
      with open(filename, "w") as f:
        f.write(content)
    except Exception as e:
      logger.error("Error while saving file: %s - exception: %s" % (filename, e))
      return False
    return filename

  def processDataForLLM(self, text_to_review: str, action: str = ""):
    # get rid of all white spaces
    text_to_review = re.sub(r"\n", " ", text_to_review)
    text_to_review = re.sub(r"\s+", " ", text_to_review)
    text_to_review = text_to_review.strip()

    if action == "summary":
      text_splitter = NLTKTextSplitter()
      texts = text_splitter.split_text(text_to_review)
      docs = [Document(page_content=t) for t in texts[:self.MAX_LIMIT_TEXT_FOR_SUMMARY]]
      return docs

    return text_to_review

  # this is just placeholder - because there is no job_status
  # this is case where external API provides just ready file (we set ready_file in output)
  async def job_status(self, job_id):
    return {'success': True, 'message': { "status": "completed" }, "code": 200 }

  async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False, params: dict = {}):
    # we know through pydantic that assetInput is a list
    if len(assetInput) > 0:
      # so it can be either string or list of strings, for example:
      # url when using rewrite/summary
      # or dict (coming from chat in form of memory)
      if isinstance(assetInput[0], str):
        # if it is string - lets check if it is url - and if so - lets download it
        if assetInput[0].startswith("http"):
          # sometimes assetInput will be just text , but sometimes it will be link (or list of links)
          # so in such case - lets download it
          downloaded = await downloadContentFromURL(assetInput)
          downloaded = downloaded['message']
          # change it to list - as this is expect in other places (i'm sure there are no \n in downloaded string)
          assetInput = downloaded.split("\n")
      elif isinstance(assetInput[0], dict):
        logger.debug("this is the case with chat !!!")
      else:
        logger.info("this is the case with WTF!!!!!! - i dont know why it's here and shouldn't be")

    # OPTIONS
    self.set_settings(userSettings)

    if action == "generate" or action == "summary" or action == "rewrite":
      return await self.tools(action, userInput, assetInput, customerId, requestId, userSettings, returnTestData)
    # if this is called - it means that chat streaming was completed and we just want to store result in DB
    elif action == "chat":
      # two cases from react - chat_completed - when streaming is on and we just want to record result
      # or no stream and then normal traditional generate
      if userInput.get("type") == "chat_no_stream":
        return await self.chat_no_stream(userInput, assetInput, customerId, requestId, userSettings, returnTestData)
      else:
        return await self.chat_completed(userInput, assetInput, customerId, requestId, userSettings, returnTestData)
    elif action == "job_status":
      return await self.job_status(userInput)
    else:
      return { "success": False, "message": "Unknown action", "code": 400 }

  async def tools(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False):
    logger.debug("OpenAITextGenerator tools - start")

    try:
      if returnTestData:
        response = "TEST text! (test data from %s)" % action
      else:
        prompt = userInput.get('prompt')
        numberOfWords = userInput.get('numberOfWords')
        #self.temperature = userInput.get('temperature') if userInput.get('temperature') else 0

        if action == "summary" or action == "rewrite":
          docs = self.processDataForLLM(assetInput[0], action)

        userMessage = f"Additional instructions: {prompt}" if prompt else ""
        lengthInstructions = "" if numberOfWords == 0 else f"{numberOfWords}-words"

        # special case for summary if not specified number of words
        if action == "summary" and lengthInstructions == "":
          lengthInstructions = "concise"

        if action != "generate":
          prompt_template = getTextPromptTemplate(action)['template']
          logger.info(prompt_template)
          PROMPT = PromptTemplate(template=prompt_template, input_variables=["text", "userMessage", "lengthInstructions"])
        if action == "summary":
          chain = load_summarize_chain(self.llm, chain_type="stuff", verbose=True, prompt=PROMPT)
          response = chain.run({"input_documents": docs, "userMessage": userMessage, "lengthInstructions": lengthInstructions})
        elif action == "rewrite":
          chain = LLMChain(prompt=PROMPT, llm=self.llm, verbose=True)
          response = chain.predict(text=docs, userMessage=userMessage, lengthInstructions=lengthInstructions)
        elif action == "generate":
          response = self.llm([HumanMessage(content=prompt)])
          response = response.content
        else:
          return {'code': 500, 'success': False, 'message': "Unknown action" }

        logger.info(f"OpenAITextGenerator - response: {response}")

      if self.save_to_file:
        filename = self.save2file(response, customerId, requestId)
        if not filename:
          return {'code': 500, 'success': False, 'message': "Error while saving file" }

      logger.debug("OpenAITextGenerator.summary() - end")

      return {'code': 200, 'success': True, 'message': { "status": "completed", "result_type": "ready_file", "result": filename, "result2": response }}
    except Exception as e:
      logger.error("Error while making API call to OpenAI - exception ")
      logger.error(e)
      traceback.print_exc()
      return {'code': 500, 'success': False, 'message': str(e) }

  # NO STREAMING MODE
  async def chat_no_stream(self, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False):
    logger.debug("OpenAITextGenerator.chat() - start")
    try:
      if returnTestData:
        final_prompt = prepareFinalPromptForChat(userInput, assetInput, self.memory_token_limit, self.prompt_total_limit, self.model_name)
        logger.info("!!!!!!!!!!!!")
        logger.info(final_prompt)
        response = "Hello! nice to meet you my friend. (Test result from chat)"
      else:

        final_prompt = prepareFinalPromptForChat(userInput, assetInput, self.memory_token_limit, self.prompt_total_limit, self.model_name)
        logger.info("model in use: %s" % self.llm)
        response = await self.llm.agenerate([final_prompt])
        #generations=[[ChatGeneration(text='Hi there! How can I assist you today?', generation_info=None, message=AIMessage(content='Hi there! How can I assist you today?', additional_kwargs={}))]] llm_output={'token_usage': {'prompt_tokens': 250, 'completion_tokens': 10, 'total_tokens': 260}, 'model_name': 'gpt-3.5-turbo'}
        # get content from response
        response = response.generations[0][0].text

      logger.info(f"OpenAITextGenerator - response: {response}")
      filename = None
      if self.save_to_file:
        filename = self.save2file(response, customerId, requestId)

        #filename = self.save2file(response, 11, 1)

        if not filename:
          return {'code': 500, 'success': False, 'message': "Error while saving file" }
      logger.debug("OpenAITextGenerator - end")

      return {'code': 200, 'success': True, 'message': { "status": "completed", "result_type": "ready_file", "result": filename, "content": response }}

    except Exception as e:
      logger.error("Error while making API call to OpenAI - exception ")
      logger.error(e)
      traceback.print_exc()
      return {'code': 500, 'success': False, 'message': str(e) }

  # STREAMING MODE - needed to register chat in DB - after successful generation
  async def chat_completed(self, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False):
    logger.debug("OpenAITextGenerator.chat() - start")
    resultForDB = userInput['resultForDB']

    filename = self.save2file(resultForDB, customerId, requestId)
    if not filename:
      return {'code': 500, 'success': False, 'message': "Error while saving file" }
    logger.debug("OpenAITextGenerator - end")

    return {'code': 200, 'success': True, 'message': { "status": "completed", "result_type": "ready_file", "result": filename, "content": resultForDB }}

  # STREAMING MODE
  def send_message(self, userInput: dict, assetInput: dict, userSettings: dict) -> Callable[[Sender], Awaitable[None]]:
    async def generate(send: Sender):
      # update settings - especially callback manager, but also model name etc
      self.callback_manager = AsyncCallbackManager([AsyncStreamCallbackHandler(send)])
      self.streamingOn = True
      self.set_settings(userSettings)

      final_prompt = prepareFinalPromptForChat(userInput, assetInput, self.memory_token_limit, self.prompt_total_limit, self.model_name)

      logger.info("model in use: %s" % self.llm)

      await self.llm.agenerate([final_prompt])

    return generate

  def stream_response(self, body: MediaModel) -> StreamingResponse:
    try:
      return ChatStreamingResponse(self.send_message(body.userInput, body.assetInput, body.userSettings), media_type="text/event-stream")
    except Exception as e:
      logger.error("Error while making API call to OpenAI - exception ")
      logger.error(e)
      traceback.print_exc()
      return StreamingResponse(status_code=500, content=str(e))