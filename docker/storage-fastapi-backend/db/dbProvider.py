from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from pydanticValidation.db_schemas import ChatMessage, ChatSession, User
import config
import uuid, os
from datetime import datetime, date, time
import json, bcrypt
import traceback
from tenacity import retry, stop_after_attempt, wait_fixed


from sqlalchemy import create_engine, MetaData, func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import logconfig
import config as config

logger = logconfig.logger

DATABASE_URL = f"mysql+aiomysql://{config.defaults['MYSQL_USER']}:{config.defaults['MYSQL_PASSWORD']}@{config.defaults['MYSQL_HOST']}/{config.defaults['MYSQL_DB']}"

# Create async engine and session
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_recycle=1800,  # Recycle connections after 1800 seconds (30 minutes)
    pool_pre_ping=True  # Enable pre-ping to check connections before using them
)


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
            self.aws_region = user_settings["aws_region"]

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

    try:
      if action == "db_new_session":
        return await self.create_new_chat_session(userInput, customerId)
      elif action == "db_new_message":
        return await self.create_chat_message(userInput, customerId)
      elif action == "db_edit_message":
        return await self.edit_chat_message_for_user(userInput, customerId)
      elif action == "db_all_sessions_for_user":
        return await self.get_all_chat_sessions_for_user(userInput, customerId)
      elif action == "db_get_user_session":
        return await self.get_chat_session(userInput, customerId)
      elif action == "db_search_messages":
        return await self.search_chat_messages_for_user(userInput, customerId)
      elif action == "db_update_session":
        return await self.update_chat_session(userInput, customerId)
      elif action == "db_remove_session":
        return await self.remove_chat_session(userInput, customerId)
      elif action == "db_auth_user":
        return await self.authenticate_user(userInput, customerId)
      else:
        raise HTTPException(status_code=400, detail="Unknown action")
    except Exception as e:
      logger.error("Error processing DB request: %s", str(e))
      raise HTTPException(status_code=500, detail="Error processing DB request")

  # TEST as sometimes db_new_session fails
  #@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
  async def create_new_chat_session(self, userInput: dict, customerId: int):
    async with AsyncSessionLocal() as session:
      async with session.begin():
        try:
          session_name = userInput.get('session_name', "New chat")
          ai_character_name = userInput.get('ai_character_name', "Assistant")
          chat_history = userInput.get('chat_history', [])

          new_session_id = await self._create_new_chat_session_internal(session, customerId, session_name, ai_character_name, chat_history)

          await session.commit()
          return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": new_session_id}}, status_code=200)
        except Exception as e:
          logger.error("Error in create_new_chat_session: %s", str(e))
          traceback.print_exc()
          #return JSONResponse(content={"False": True, "code": 400, "message": {"status": "fail", "result": str(e)}}, status_code=400)
          raise HTTPException(status_code=500, detail="Error in DB! create_new_chat_session")

  async def create_chat_message(self, userInput: dict, customerId: int):
    async with AsyncSessionLocal() as session:
      async with session.begin():
        try:
          # Check if session_id is set, if not create a new session
          if not userInput.get('session_id'):
            userInput['session_id'] = await self._create_new_chat_session_internal(session, customerId)

          userMessage = userInput['userMessage']
          aiResponse = userInput['aiResponse']

          # first create new item for user message in chat message
          new_user_message = ChatMessage(
            session_id=userInput['session_id'],
            customer_id=customerId,
            sender=userMessage['sender'],
            message=userMessage['message'],
            image_locations=userMessage.get('image_locations'),
            file_locations=userMessage.get('file_locations')
          )
          session.add(new_user_message)

          # Commit to generate message_id
          await session.flush()

          new_user_message_id = new_user_message.message_id

          new_ai_response_id = 0
          # if its not error message (because it means we dont have AI response)
          if aiResponse['message'] != config.defaults['ERROR_MESSAGE_FOR_TEXT_GEN']:
            # first create new item in chat message
            new_ai_response = ChatMessage(
              session_id=userInput['session_id'],
              customer_id=customerId,
              sender=aiResponse['sender'],
              message=aiResponse['message'],
              image_locations=aiResponse.get('image_locations'),
              file_locations=aiResponse.get('file_locations')
            )
            session.add(new_ai_response)

            # Commit to generate message_id
            await session.flush()

            new_ai_response_id = new_ai_response.message_id

          logger.info("New messages IDs. User: %s, AI: %s", new_user_message_id, new_ai_response_id)

          # Update chat session's chat_history and last_update
          chat_session = await session.get(ChatSession, userInput['session_id'])
          if chat_session:
            # Use chat_history from userInput directly
            chat_history = userInput['chat_history']

            # Update the last 2 messages in chat history with the new user and AI message_id (very important because later we save chat history in chat sessions for future restore)
            if chat_history and isinstance(chat_history[-2], dict):
                chat_history[-2]['messageId'] = new_user_message_id
            # > 0 - to check if there was no error message (because then we dont need to do anything)
            if chat_history and isinstance(chat_history[-1], dict) and new_ai_response_id > 0:
                chat_history[-1]['messageId'] = new_ai_response_id

            chat_session.chat_history = json.dumps(chat_history)

            # OK this probably could have been done better and from different place, but well...
            # we check first few messages in history (so later, in case of long chats - we skip simply this step and its minimally quicker)
            # and then we get oldest AI message and read AI character... so we can set it as default for this chat (so later it will be displayed in chat lists on top left menu)
            if len(chat_history) < 4:
              # Find the oldest AI message
              for message in chat_history:
                if not message.get('isUserMessage'):
                  ai_character_name = message.get('aiCharacterName')
                  if ai_character_name:
                    chat_session.ai_character_name = ai_character_name
                    break
            chat_session.last_update = func.now()
          else:
            raise HTTPException(status_code=404, detail="Chat session not found")

          result = await session.commit()
          logger.info("Result of commit: %s", result)

          return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": { "userMessageId": new_user_message_id, "aiMessageId": new_ai_response_id}, "sessionId": userInput['session_id'] }}, status_code=200)
        except HTTPException as e:
          logger.error("HTTP error in create_chat_message: %s", str(e))
          traceback.print_exc()
          #return JSONResponse(status_code=e.status_code, content={"success": False, "code": e.status_code, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! create_chat_message"}})
          raise HTTPException(status_code=500, detail="Error in DB! create_chat_message")
        except Exception as e:
          logger.error("Error in DB! create_chat_message: %s", str(e))
          traceback.print_exc()
          #return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! create_chat_message"}}, status_code=500)
          raise HTTPException(status_code=500, detail="Error in DB! create_chat_message")

  async def edit_chat_message_for_user(self, userInput: dict, customerId: int):
    async with AsyncSessionLocal() as session:
      async with session.begin():
        try:
          userMessage = userInput['userMessage']
          aiResponse = userInput['aiResponse']

          user_message_id = userMessage['message_id']

          # Check if the message exists and belongs to the user
          db_user_message = await session.get(ChatMessage, user_message_id)
          if not db_user_message:
              raise HTTPException(status_code=404, detail="Message not found")
          if db_user_message.customer_id != customerId:
              raise HTTPException(status_code=403, detail="Not authorized to edit this message")

          # Update the message text
          db_user_message.message = userMessage['message']
          db_user_message.image_locations = userMessage['image_locations']
          db_user_message.file_locations = userMessage['file_locations']

          ai_message_id = aiResponse['message_id']

          # Check if the message exists and belongs to the user
          db_ai_message = await session.get(ChatMessage, ai_message_id)
          if not db_ai_message:
              raise HTTPException(status_code=404, detail="Message not found")
          if db_ai_message.customer_id != customerId:
              raise HTTPException(status_code=403, detail="Not authorized to edit this message")

          # Update the message text
          db_ai_message.message = aiResponse['message']
          db_ai_message.image_locations = aiResponse['image_locations']
          db_ai_message.file_locations = aiResponse['file_locations']

          # Update chat session's chat_history and last_update
          chat_session = await session.get(ChatSession, userInput['session_id'])
          if chat_session:
            # Use chat_history from userInput directly
            chat_session.chat_history = json.dumps(userInput['chat_history'])
            chat_session.last_update = func.now()
          else:
            raise HTTPException(status_code=404, detail="Chat session not found")

          await session.commit()
          return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": "Edit completed"}}, status_code=200)
        except Exception as e:
          logger.error("Error in DB! edit_chat_message_for_user: %s", str(e))
          traceback.print_exc()
          #return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! edit_chat_message_for_user"}}, status_code=500)
          raise HTTPException(status_code=500, detail="Error in DB! edit_chat_message_for_user")

  async def get_all_chat_sessions_for_user(self, userInput: dict, customerId: int):
    offset = userInput.get('offset', 0)
    limit = userInput.get('limit', 30)
    async with AsyncSessionLocal() as session:
      try:
        result = await session.execute(
          select(ChatSession)
          .where(
            and_(
              ChatSession.customer_id == customerId,
              func.json_length(ChatSession.chat_history) > 0
            )
          )
          .order_by(ChatSession.last_update.desc())
          .offset(offset)
          .limit(limit)
        )

        sessions = result.scalars().all()
        sessions_list = [self.to_dict(session) for session in sessions]

        logger.debug("All sessions for user %s: %s", customerId, sessions_list)
        return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": sessions_list}}, status_code=200)
      except Exception as e:
        logger.error("Error in DB! get_all_chat_sessions_for_user: %s", str(e))
        traceback.print_exc()
        #return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! get_all_chat_sessions_for_user"}}, status_code=500)
        raise HTTPException(status_code=500, detail="Error in DB! get_all_chat_sessions_for_user")


  async def get_chat_session(self, userInput: dict, customerId: int):
    session_id = userInput['session_id']
    async with AsyncSessionLocal() as session:
      async with session.begin():
        try:
          result = await session.execute(
            select(ChatSession).where(ChatSession.session_id == session_id, ChatSession.customer_id == customerId)
          )
          chat_session = result.scalars().first()
          chat_session_content = self.to_dict(chat_session)
          logger.info("Chat session %s: %s", session_id, chat_session_content)
          if chat_session is None:
            raise HTTPException(status_code=404, detail="Chat session not found")
          return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": chat_session_content}}, status_code=200)
        except Exception as e:
          logger.error("Error in DB! get_chat_session: %s", str(e))
          traceback.print_exc()
          #return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! get_chat_session"}}, status_code=500)
          raise HTTPException(status_code=500, detail="Error in DB! get_chat_session")


  async def search_chat_messages_for_user(self, userInput: dict, customerId: int):
    search_text = userInput['search_text']
    async with AsyncSessionLocal() as session:
      async with session.begin():
        try:
          stmt = select(ChatSession).join(ChatMessage).where(
            ChatMessage.customer_id == customerId,
            ChatMessage.message.ilike(f"%{search_text}%")
          ).order_by(ChatSession.last_update.desc())
          result = await session.execute(stmt)
          messages = result.scalars().all()
          sessions_list = [self.to_dict(message) for message in messages] 

          logger.info("All sessions with search message for user %s: %s", customerId, sessions_list)
          #logger.info("All session ids for user %s: %s", customer_id, session_ids)
          return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": sessions_list}}, status_code=200)
        except Exception as e:
          logger.error("Error in DB! search_chat_messages_for_user: %s", str(e))
          traceback.print_exc()
          #return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! search_chat_messages_for_user"}}, status_code=500)
          raise HTTPException(status_code=500, detail="Error in DB! search_chat_messages_for_user")

  async def update_chat_session(self, userInput: dict, customerId: int):
    session_id = userInput['session_id']
    new_session_name = userInput.get('new_session_name')
    new_ai_character_name = userInput.get('new_ai_character_name')
    chat_history = userInput.get('chat_history')
    async with AsyncSessionLocal() as session:
      async with session.begin():
        try:
          result = await session.execute(
            select(ChatSession).where(ChatSession.session_id == session_id, ChatSession.customer_id == customerId)
          )
          chat_session = result.scalars().first()
          if chat_session is None:
            raise HTTPException(status_code=404, detail="Chat session not found")
          if new_session_name:
            chat_session.session_name = new_session_name
          if new_ai_character_name:
            chat_session.ai_character_name = new_ai_character_name
          if chat_history:
            chat_session.chat_history = json.dumps(chat_history)
          chat_session.last_update = func.now()
          await session.commit()
          return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": "Session updated"}}, status_code=200)
        except Exception as e:
          logger.error("Error in DB! update_chat_session: %s", str(e))
          traceback.print_exc()
          raise HTTPException(status_code=500, detail="Error in DB! update_chat_session")

  async def remove_chat_session(self, userInput: dict, customerId: int):
    session_id = userInput.get('session_id')
    if not session_id:
      raise HTTPException(status_code=400, detail="session_id is required")

    async with AsyncSessionLocal() as session:
      async with session.begin():
        try:
          # Delete all messages associated with the session
          await session.execute(
              select(ChatMessage).where(ChatMessage.session_id == session_id)
          )
          await session.execute(
              ChatMessage.__table__.delete().where(ChatMessage.session_id == session_id)
          )

          # Delete the session
          result = await session.execute(
              select(ChatSession).where(ChatSession.session_id == session_id, ChatSession.customer_id == customerId)
          )
          chat_session = result.scalars().first()
          if chat_session is None:
              raise HTTPException(status_code=404, detail="Chat session not found")

          await session.delete(chat_session)
          await session.commit()

          return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": "Session removed"}}, status_code=200)
        except Exception as e:
          logger.error("Error in DB! remove_chat_session: %s", str(e))
          traceback.print_exc()
          raise HTTPException(status_code=500, detail="Error in DB! remove_chat_session")

  # Helper function to create a new chat session (it's used in two diff functions)
  async def _create_new_chat_session_internal(self, session, customerId: int, session_name: str = "New chat", ai_character_name: str = "Assistant", chat_history: list = []):
    new_session = ChatSession(
      session_id=str(uuid.uuid4()),
      customer_id=customerId,
      session_name=session_name,
      ai_character_name=ai_character_name,
      chat_history=chat_history
    )
    session.add(new_session)
    await session.flush()
    logger.info("New session ID: %s", new_session.session_id)
    return new_session.session_id

  async def authenticate_user(self, userInput: dict, customerId: int):
    async with AsyncSessionLocal() as session:
      async with session.begin():
        try:
          username = userInput['username']
          password = userInput['password']

          result = await session.execute(
            select(User).where(
              User.email == username,
              User.customer_id == customerId
              )
          )

          user = result.scalars().first()

          if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": { "result": "User authenticated", "token": os.environ.get('MY_AUTH_TOKEN', None) }}}, status_code=200)
          else:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        except Exception as e:
          logger.error("Error in authenticate_user: %s", str(e))
          traceback.print_exc()
          raise HTTPException(status_code=500, detail="Error in DB! authenticate_user")
