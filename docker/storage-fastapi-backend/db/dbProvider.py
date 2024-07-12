from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydanticValidation.db_schemas import ChatMessage, ChatSession, User
import config
import uuid
import os
import bcrypt
import traceback
# from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime

from sqlalchemy import create_engine, MetaData, func, select, and_, or_, distinct, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import logconfig
import config as config

from db.dbGarminHealth import *
from db.dbHelper import to_dict

logger = logconfig.logger

DATABASE_URL = f"mysql+aiomysql://{config.defaults['MYSQL_USER']}:{config.defaults['MYSQL_PASSWORD']}@{config.defaults['MYSQL_HOST']}/{config.defaults['MYSQL_DB']}"

# Create async engine and session
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
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
        self.aws_region = "eu-west-1"  # not in use

    def set_settings(self, user_settings={}):
        if user_settings:
            # and now process aws settings (doubt it will be used)
            # this is not in use - just for maybe future
            user_settings = user_settings.get("aws", {})
            # Update model name
            if "aws_region" in user_settings:
                self.aws_region = user_settings["aws_region"]

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)

        try:
            if action == "db_new_session":
                return await self.db_new_session(userInput, customerId)
            elif action == "db_new_message":
                return await self.db_new_message(userInput, customerId, userSettings)
            elif action == "db_edit_message":
                return await self.db_edit_message(userInput, customerId)
            elif action == "db_all_sessions_for_user":
                return await self.db_all_sessions_for_user(userInput, customerId)
            elif action == "db_get_user_session":
                return await self.db_get_user_session(userInput, customerId)
            elif action == "db_search_messages":
                return await self.db_search_messages(userInput, customerId)
            elif action == "db_update_session":
                return await self.db_update_session(userInput, customerId)
            elif action == "db_remove_session":
                return await self.db_remove_session(userInput, customerId)
            elif action == "db_auth_user":
                return await self.db_auth_user(userInput, customerId)
            # GARMIN HEALTH DATA (separated file)
            elif action == "insert_sleep_data":
                return await insert_sleep_data(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_user_summary":
                return await insert_user_summary(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_body_composition":
                return await insert_body_composition(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_hrv_data":
                return await insert_hrv_data(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_training_readiness":
                return await insert_training_readiness(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_endurance_score":
                return await insert_endurance_score(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_training_status":
                return await insert_training_status(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_max_metrics":
                return await insert_max_metrics(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_training_load_balance":
                return await insert_training_load_balance(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_fitness_age":
                return await insert_fitness_age(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_activity_data":
                return await insert_activity_data(AsyncSessionLocal, userInput, customerId)
            elif action == "insert_activity_gps_data":
                return await insert_activity_gps_data(AsyncSessionLocal, userInput, customerId)
            elif action == "get_garmin_data":
                return await get_garmin_data(AsyncSessionLocal, userInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing DB request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing DB request")

    # TEST as sometimes db_new_session fails
    # @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def db_new_session(self, userInput: dict, customerId: int):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    date_now = datetime.now().strftime("%Y-%m-%d")
                    session_name = userInput.get(
                        'session_name', "New chat %s" % date_now)
                    ai_character_name = userInput.get(
                        'ai_character_name', "assistant")

                    chat_history = userInput.get('chat_history', [])

                    new_session_id = await self._db_new_session_internal(session, customerId, session_name, ai_character_name, chat_history)

                    await session.commit()
                    return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": new_session_id}}, status_code=200)
                except Exception as e:
                    logger.error("Error in db_new_session: %s", str(e))
                    traceback.print_exc()
                    # return JSONResponse(content={"False": True, "code": 400, "message": {"status": "fail", "result": str(e)}}, status_code=400)
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_new_session")

    async def db_new_message(self, userInput: dict, customerId: int, userSettings: dict = {}):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    logger.info("!*" * 30)
                    logger.info("userInput : " + str(userInput))
                    logger.info("userSettings : " + str(userSettings))

                    # Check if session_id is set, if not create a new session
                    if not userInput.get('session_id'):
                        ai_character = userSettings.get(
                            'text', {}).get('ai_character', 'assistant')
                        # date now in format YYYY-MM-DD
                        date_now = datetime.now().strftime("%Y-%m-%d")
                        userInput['session_id'] = await self._db_new_session_internal(session, customerId, session_name="New chat %s" % date_now, ai_character_name=ai_character)

                    userMessage = userInput['userMessage']
                    aiResponse = userInput.get('aiResponse')

                    new_user_message = ChatMessage(
                        session_id=userInput['session_id'],
                        customer_id=customerId,
                        sender=userMessage['sender'],
                        message=userMessage['message'],
                        image_locations=userMessage.get('image_locations'),
                        file_locations=userMessage.get('file_locations')
                    )
                    session.add(new_user_message)
                    await session.flush()
                    new_user_message_id = new_user_message.message_id

                    new_ai_response_id = 0
                    if aiResponse and aiResponse['message'] != config.defaults['ERROR_MESSAGE_FOR_TEXT_GEN']:
                        new_ai_response = ChatMessage(
                            session_id=userInput['session_id'],
                            customer_id=customerId,
                            sender=aiResponse['sender'],
                            message=aiResponse['message'],
                            image_locations=aiResponse.get('image_locations'),
                            file_locations=aiResponse.get('file_locations')
                        )
                        session.add(new_ai_response)
                        await session.flush()
                        new_ai_response_id = new_ai_response.message_id

                    chat_session = await session.get(ChatSession, userInput['session_id'])
                    if chat_session:
                        chat_history = userInput['chat_history']

                        userMessageIndex = -2
                        if not aiResponse:
                            userMessageIndex = -1
                        if chat_history and isinstance(chat_history[userMessageIndex], dict):
                            chat_history[userMessageIndex]['messageId'] = new_user_message_id
                        if chat_history and isinstance(chat_history[-1], dict) and new_ai_response_id > 0:
                            chat_history[-1]['messageId'] = new_ai_response_id

                        chat_session.chat_history = chat_history

                        # this is to set AI character for session. I think it will not be used at all (there are only few small cases)
                        # because it should be set when new db session is set
                        chat_session_ai_character = ""
                        # verify first few AI messages
                        if len(chat_history) < 3:
                            for message in chat_history:
                                if not message.get('isUserMessage'):
                                    ai_character_name = message.get(
                                        'aiCharacterName')
                                    if ai_character_name:
                                        chat_session_ai_character = ai_character_name
                                        break

                        # but if it's set already - let's leave it as is (important! because we don't want to overwrite if we have one time message to different character - using @)
                        if chat_session.ai_character_name != "":
                            chat_session_ai_character = chat_session.ai_character_name

                        if chat_session_ai_character == "":
                            if userSettings['text'].get('ai_character'):
                                chat_session.ai_character_name = userSettings['text'].get(
                                    'ai_character')
                        else:
                            chat_session.ai_character_name = chat_session_ai_character
                        chat_session.last_update = func.now()
                    else:
                        raise HTTPException(
                            status_code=404, detail="Chat session not found")

                    result = await session.commit()
                    logger.debug("Result of commit: %s", result)

                    return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": {"userMessageId": new_user_message_id, "aiMessageId": new_ai_response_id, "sessionId": userInput['session_id']}}}, status_code=200)
                except HTTPException as e:
                    logger.error("HTTP error in db_new_message: %s", str(e))
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_new_message")
                except Exception as e:
                    logger.error("Error in DB! db_new_message: %s", str(e))
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_new_message")

    async def db_edit_message(self, userInput: dict, customerId: int):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    userMessage = userInput['userMessage']
                    # might be null (for example for chats without AI response)
                    aiResponse = userInput.get('aiResponse')

                    user_message_id = userMessage['message_id']

                    # Check if the message exists and belongs to the user
                    db_user_message = await session.get(ChatMessage, user_message_id)
                    if not db_user_message:
                        raise HTTPException(
                            status_code=404, detail="Message not found")
                    if db_user_message.customer_id != customerId:
                        raise HTTPException(
                            status_code=403, detail="Not authorized to edit this message")

                    # Update the message text
                    db_user_message.message = userMessage['message']
                    db_user_message.image_locations = userMessage['image_locations']
                    db_user_message.file_locations = userMessage['file_locations']

                    # let's check if we have AI response's message_id
                    # (there is a case where AI response fails and there is no message_id
                    # or aiResponse might be null - as mentioned above)
                    ai_message_id = aiResponse.get(
                        'message_id', 0) if aiResponse else 0
                    new_ai_message_id = 0

                    # Check if the message exists and belongs to the user
                    if ai_message_id:
                        db_ai_message = await session.get(ChatMessage, ai_message_id)
                    else:
                        db_ai_message = None

                    if aiResponse:
                        if not db_ai_message:
                            # If AI message does not exist, create a new one - important for history restore and search
                            new_ai_message = ChatMessage(
                                session_id=userInput['session_id'],
                                customer_id=customerId,
                                sender=aiResponse['sender'],
                                message=aiResponse['message'],
                                image_locations=aiResponse.get(
                                    'image_locations'),
                                file_locations=aiResponse.get('file_locations')
                            )
                            session.add(new_ai_message)
                            await session.flush()  # Generate the new message ID
                            new_ai_message_id = new_ai_message.message_id

                            # Update the last AI message in the chat history with the new ID
                            if userInput['chat_history']:
                                for message in reversed(userInput['chat_history']):
                                    if not message.get('isUserMessage'):
                                        message['messageId'] = new_ai_message_id
                                        break
                        else:
                            # if everything as it should be and there is message_id to be edited
                            # Update the existing AI message
                            db_ai_message.message = aiResponse['message']
                            db_ai_message.image_locations = aiResponse['image_locations']
                            db_ai_message.file_locations = aiResponse['file_locations']
                            new_ai_message_id = db_ai_message.message_id

                    # Update chat session's chat_history and last_update
                    chat_session = await session.get(ChatSession, userInput['session_id'])
                    if chat_session:
                        # Use chat_history from userInput directly
                        chat_session.chat_history = userInput['chat_history']
                        chat_session.last_update = func.now()
                    else:
                        raise HTTPException(
                            status_code=404, detail="Chat session not found")

                    await session.commit()
                    return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": {"aiMessageId": new_ai_message_id, "userMessageId": user_message_id, "sessionId": userInput['session_id']}}}, status_code=200)
                except Exception as e:
                    logger.error(
                        "Error in DB! edit_chat_message_for_user: %s", str(e))
                    traceback.print_exc()
                    # return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! edit_chat_message_for_user"}}, status_code=500)
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_edit_message")

    async def db_all_sessions_for_user(self, userInput: dict, customerId: int):
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
                sessions_list = [to_dict(session) for session in sessions]

                return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": sessions_list}}, status_code=200)
            except Exception as e:
                logger.error(
                    "Error in DB! db_all_sessions_for_user: %s", str(e))
                traceback.print_exc()
                # return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! get_all_chat_sessions_for_user"}}, status_code=500)
                raise HTTPException(
                    status_code=500, detail="Error in DB! db_all_sessions_for_user")

    async def db_get_user_session(self, userInput: dict, customerId: int):
        session_id = userInput['session_id']
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    result = await session.execute(
                        select(ChatSession).where(ChatSession.session_id ==
                                                  session_id, ChatSession.customer_id == customerId)
                    )
                    chat_session = result.scalars().first()
                    chat_session_content = to_dict(chat_session)
                    logger.debug("Chat session %s: %s",
                                 session_id, chat_session_content)
                    if chat_session is None:
                        raise HTTPException(
                            status_code=404, detail="Chat session not found")
                    return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": chat_session_content}}, status_code=200)
                except Exception as e:
                    logger.error(
                        "Error in DB! db_get_user_session: %s", str(e))
                    traceback.print_exc()
                    # return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! get_chat_session"}}, status_code=500)
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_get_user_session")

    async def db_search_messages(self, userInput: dict, customerId: int):
        search_text = userInput['search_text']
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    stmt = select(ChatSession).distinct(ChatSession.session_id).join(ChatMessage).where(
                        ChatMessage.customer_id == customerId,
                        or_(
                            ChatMessage.message.ilike(f"%{search_text}%"),
                            ChatSession.session_name.ilike(f"%{search_text}%")
                        )
                    ).order_by(ChatSession.last_update.desc())
                    result = await session.execute(stmt)
                    messages = result.scalars().all()
                    sessions_list = [to_dict(message)
                                     for message in messages]

                    # logger.debug("All sessions with search message for user %s: %s", customerId, sessions_list)

                    return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": sessions_list}}, status_code=200)
                except Exception as e:
                    logger.error("Error in DB! db_search_messages: %s", str(e))
                    traceback.print_exc()
                    # return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! search_chat_messages_for_user"}}, status_code=500)
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_search_messages")

    async def db_update_session(self, userInput: dict, customerId: int):
        session_id = userInput['session_id']
        new_session_name = userInput.get('new_session_name')
        new_ai_character_name = userInput.get('new_ai_character_name')
        chat_history = userInput.get('chat_history')

        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    result = await session.execute(
                        select(ChatSession).where(ChatSession.session_id ==
                                                  session_id, ChatSession.customer_id == customerId)
                    )
                    chat_session = result.scalars().first()
                    if chat_session is None:
                        raise HTTPException(
                            status_code=404, detail="Chat session not found")
                    if new_session_name:
                        chat_session.session_name = new_session_name
                    if new_ai_character_name:
                        chat_session.ai_character_name = new_ai_character_name
                    if chat_history:
                        chat_session.chat_history = chat_history
                    chat_session.last_update = func.now()
                    await session.commit()
                    return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": "Session updated"}}, status_code=200)
                except Exception as e:
                    logger.error("Error in DB! db_update_session: %s", str(e))
                    # traceback.print_exc()
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_update_session")

    async def db_remove_session(self, userInput: dict, customerId: int):
        session_id = userInput.get('session_id')
        if not session_id:
            raise HTTPException(
                status_code=400, detail="session_id is required")

        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    # Delete all messages associated with the session
                    await session.execute(
                        select(ChatMessage).where(
                            ChatMessage.session_id == session_id)
                    )
                    await session.execute(
                        ChatMessage.__table__.delete().where(ChatMessage.session_id == session_id)
                    )

                    # Delete the session
                    result = await session.execute(
                        select(ChatSession).where(ChatSession.session_id ==
                                                  session_id, ChatSession.customer_id == customerId)
                    )
                    chat_session = result.scalars().first()
                    if chat_session is None:
                        raise HTTPException(
                            status_code=404, detail="Chat session not found")

                    await session.delete(chat_session)
                    await session.commit()

                    return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": "Session removed"}}, status_code=200)
                except Exception as e:
                    logger.error("Error in DB! db_remove_session: %s", str(e))
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_remove_session")

    # Helper function to create a new chat session (it's used in two diff functions)
    async def _db_new_session_internal(self, session, customerId: int, session_name: str = "New chat", ai_character_name: str = "assistant", chat_history: list = []):
        new_session = ChatSession(
            session_id=str(uuid.uuid4()),
            customer_id=customerId,
            session_name=session_name,
            ai_character_name=ai_character_name,
            chat_history=chat_history
        )
        logger.info("ai character: %s", ai_character_name)
        session.add(new_session)

        await session.flush()
        logger.debug("New session ID: %s", new_session.session_id)
        return new_session.session_id

    async def db_auth_user(self, userInput: dict, customerId: int):
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
                        return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": {"result": "User authenticated", "token": os.environ.get('MY_AUTH_BEARER_TOKEN', None)}}}, status_code=200)
                    else:
                        raise HTTPException(
                            status_code=401, detail="Invalid username or password")
                except Exception as e:
                    logger.error("Error in db_auth_user: %s", str(e))
                    traceback.print_exc()
                    raise HTTPException(
                        status_code=500, detail="Error in DB! db_auth_user")
