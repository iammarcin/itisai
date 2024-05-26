from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from pydanticValidation.db_schemas import ChatMessage, ChatSession, User
import config
import uuid
from datetime import datetime, date, time
import json

from sqlalchemy import create_engine, MetaData, func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import logconfig

logger = logconfig.logger

DATABASE_URL = f"mysql+aiomysql://{config.defaults['MYSQL_USER']}:{config.defaults['MYSQL_PASSWORD']}@{config.defaults['MYSQL_HOST']}/{config.defaults['MYSQL_DB']}"

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

class dbProvider:
  def __init__(self):
    self.aws_region = "eu-west-1" # not in use

  def set_settings(self, user_settings={}):
    if user_settings:
        # and now process aws settings (doubt it will be used)
        # this is not in use - just for maybe future
        user_settings = user_settings.get("aws", {})
        # Update model name
        if "aws_region" in user_settings:
            user_settings["aws_region"] = user_settings["aws_region"]

  # this is needed to serialize the data from the database
  # alchemy has its own structure and if we just put the object into JSON it will not work
  def to_dict(self, instance):
    if instance is None:
        return None
    result = {}
    for column in instance.__table__.columns:
        value = getattr(instance, column.name)
        if isinstance(value, (datetime, date, time)):
            value = value.isoformat()
        elif isinstance(value, dict):
            value = json.dumps(value)  # Ensure nested dictionaries are serialized properly
        result[column.name] = value
    return result


  async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
    # OPTIONS
    self.set_settings(userSettings)

    if action == "db_new_session":
      return await self.create_new_chat_session(userInput, customerId)
    elif action == "db_all_sessions_for_user":
      return await self.get_all_chat_sessions_for_user(customerId)
    elif action == "db_user_session":
      return await self.get_chat_session(userInput['session_id'], customerId)
    elif action == "db_new_message":
      return await self.create_chat_message(userInput)
    '''
    elif action == "db_search_messages":
        return self.search_chat_messages_for_user(userInput['customer_id'], userInput['search_text'])
    else:
        raise HTTPException(status_code=400, detail="Unknown action")
    '''

  async def create_new_chat_session(self, userInput: dict, customerId: int):
    async with AsyncSessionLocal() as session:
      async with session.begin():
        new_session = ChatSession(
          session_id=str(uuid.uuid4()),
          customer_id=customerId,
          session_name=userInput.get('session_name', "New chat"),
          chat_history=userInput.get('chat_history', [])
        )
        session.add(new_session)
        await session.commit()
        logger.info("New session ID: %s", new_session.session_id)
        return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": new_session.session_id}}, status_code=200)

  async def get_all_chat_sessions_for_user(self, customer_id: int):
    async with AsyncSessionLocal() as session:
      result = await session.execute(
        select(ChatSession).where(ChatSession.customer_id == customer_id)
      )
      sessions = result.scalars().all()
      sessions_list = [self.to_dict(session) for session in sessions]

      logger.info("All sessions for user %s: %s", customer_id, sessions_list)
      return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": sessions_list}}, status_code=200)

  async def get_chat_session(self, session_id: str, customer_id: int):
    async with AsyncSessionLocal() as session:
      async with session.begin():
        result = await session.execute(
          select(ChatSession).where(ChatSession.session_id == session_id, ChatSession.customer_id == customer_id)
        )
        chat_session = result.scalars().first()
        chat_session_content = self.to_dict(chat_session)
        logger.info("Chat session %s: %s", session_id, chat_session_content)
        if chat_session is None:
          raise HTTPException(status_code=404, detail="Chat session not found")
        return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": chat_session_content}}, status_code=200)

  async def create_chat_message(self, userInput: dict):
      async with AsyncSessionLocal() as session:
          async with session.begin():
              # first create new item in chat message
              new_message = ChatMessage(
                  session_id=userInput['session_id'],
                  customer_id=userInput['customer_id'],
                  sender=userInput['sender'],
                  message=userInput['message'],
                  image_locations=userInput.get('image_locations'),
                  file_locations=userInput.get('file_locations')
              )
              session.add(new_message)
              logger.info("!"*100)

              # Update chat session's chat_history and last_update
              chat_session = await session.get(ChatSession, userInput['session_id'])
              if chat_session:
                  # Use chat_history from userInput directly
                  chat_session.chat_history = json.dumps(userInput['chat_history'])
                  chat_session.last_update = func.now()
              else:
                  raise HTTPException(status_code=404, detail="Chat session not found")

              '''
              chat_session = await session.get(ChatSession, userInput['session_id'])
              if chat_session:
                  #chat_history = chat_session.chat_history or []
                  #chat_history = json.loads(chat_session.chat_history) if chat_session.chat_history else []
                  chat_history = json.loads(chat_session.chat_history) if chat_session.chat_history else []
                  logger.info("chat_history: %s", chat_history)
                  logger.info("Chat history from user input: %s", userInput['chat_history'])
                  logger.info("JSON: %s", json.loads(userInput['chat_history']))
                  #chat_history.append(userInput['message'])
                  chat_item = {
                        "message": userInput['message'],
                        "isUserMessage": userInput['sender'] != "AI",  # Assuming 'sender' indicates if it's AI or user
                        "imageLocations": userInput.get('image_locations', []),
                        "fileNames": userInput.get('file_locations', []),
                        "aiCharacterImageResId": None  # This can be set based on your logic
                  }
                  chat_history.append(chat_item)
                  chat_session.chat_history = json.dumps(chat_history)
                  logger.info("chat_history: %s", chat_history)
                  #chat_session.chat_history = chat_history
                  chat_session.last_update = func.now()
                  logger.info("chat_session: %s", chat_session)
              else:
                  raise HTTPException(status_code=404, detail="Chat session not found")
              '''
              result = await session.commit()
              logger.info("Result of commit: %s", result)

              return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": result}}, status_code=200)