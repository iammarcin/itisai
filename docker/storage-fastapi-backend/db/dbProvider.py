from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from pydanticValidation.db_schemas import ChatMessage, ChatSession, User
import config
import uuid

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

  async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
    # OPTIONS
    self.set_settings(userSettings)

    if action == "db_new_session":
        return await self.create_chat_session(userInput, customerId)
    elif action == "db_get_all_sessions":
        return await self.get_all_chat_sessions_for_user(customerId)
    '''
    if action == "db_new_message":
        return self.create_chat_message(userInput)
    elif action == "db_new_session":
        return self.create_chat_session(userInput, customerId)
    elif action == "db_get_session":
        return self.get_chat_session(userInput['session_id'])
    elif action == "db_get_all_sessions":
        return self.get_all_chat_sessions_for_user(userInput['user_id'])
    elif action == "db_search_messages":
        return self.search_chat_messages_for_user(userInput['user_id'], userInput['search_text'])
    else:
        raise HTTPException(status_code=400, detail="Unknown action")
    '''
  def create_chat_message(self, userInput: dict):
    message = userInput['message']
    db = self.client
    db_message = ChatMessage(**message)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

  async def create_chat_session(self, userInput: dict, customerId: int):
      async with AsyncSessionLocal() as session:
          async with session.begin():
              new_session = ChatSession(
                  session_id=str(uuid.uuid4()),
                  user_id=customerId,
                  session_name=userInput.get('session_name'),
                  chat_history=userInput.get('chat_history', [])
              )
              session.add(new_session)
              await session.commit()
              logger.info("New session ID: %s", new_session.session_id)
              return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": new_session.session_id}}, status_code=200)

  async def create_chat_session3(self, userInput: dict, customerId: int):
      session_data = {
          'user_id': 1,
          'session_name': userInput.get('session_name', 'Default Session Name'),
          'session_id': userInput.get('session_id', str(uuid.uuid4()))
      }
      
      async with self.db as db:
          db_session = ChatSession(**session_data)
          db.add(db_session)
          await db.commit()
          await db.refresh(db_session)
          return db_session
      

  def create_chat_session2(self, userInput: dict, customerId: int):
    session_data = {}
    session_data['user_id'] = customerId
    session_data['session_name'] = userInput.get('session_name', 'New chat')
    session_data['session_id'] = userInput.get('session_id', str(uuid.uuid4()))

    db = self.client
    db_session = ChatSession(**session_data)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

  def get_chat_session(self, session_id: str):
    db = self.client
    return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

  async def get_all_chat_sessions_for_user(self, user_id: int):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ChatSession).where(ChatSession.user_id == user_id)
            )
            sessions = result.scalars().all()
            return sessions
  def get_all_chat_sessions_for_user2(self, user_id: int):
    db = self.client
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

  def search_chat_messages_for_user(self, user_id: int, search_text: str):
    db = self.client
    return db.query(ChatMessage).filter(ChatMessage.user_id == user_id, ChatMessage.message.ilike(f"%{search_text}%")).all()