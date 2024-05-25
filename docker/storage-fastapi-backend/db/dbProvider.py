from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydanticValidation.db_schemas import ChatMessage, ChatSession, User
import config
import uuid

from sqlalchemy import create_engine, MetaData, func
from sqlalchemy.orm import sessionmaker

import logconfig

logger = logconfig.logger

DATABASE_URL = f"mysql+mysqlconnector://{config.defaults['MYSQL_USER']}:{config.defaults['MYSQL_PASSWORD']}@{config.defaults['MYSQL_HOST']}/{config.defaults['MYSQL_DB']}"

metadata = MetaData()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class dbProvider:
  def __init__(self):
    self.aws_region = "eu-west-1" # not in use
    self.client = get_db()

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

    if action == "db_new_message":
        return self.create_chat_message(userInput)
    elif action == "db_new_session":
        return self.create_chat_session(userInput)
    elif action == "db_get_session":
        return self.get_chat_session(userInput['session_id'])
    elif action == "db_get_all_sessions":
        return self.get_all_chat_sessions_for_user(userInput['user_id'])
    elif action == "db_search_messages":
        return self.search_chat_messages_for_user(userInput['user_id'], userInput['search_text'])
    else:
        raise HTTPException(status_code=400, detail="Unknown action")

  def create_chat_message(self, userInput: dict):
    message = userInput['message']
    db = self.client
    db_message = ChatMessage(**message)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

  def create_chat_session(self, userInput: dict):
    session = userInput['session']
    db = self.client
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    db_session = ChatSession(**session)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

  def get_chat_session(self, session_id: str):
    db = self.client
    return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

  def get_all_chat_sessions_for_user(self, user_id: int):
    db = self.client
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

  def search_chat_messages_for_user(self, user_id: int, search_text: str):
    db = self.client
    return db.query(ChatMessage).filter(ChatMessage.user_id == user_id, ChatMessage.message.ilike(f"%{search_text}%")).all()