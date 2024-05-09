from fastapi import APIRouter, Depends
from main_auth_token import auth_user_token
from main_generators import get_generator
from pydanticValidation.general_schemas import MediaModel
from fastapi import Form, File, UploadFile
import config as config
import logconfig
import json
# chat stream
import asyncio
import traceback
from typing import Any, Optional, Awaitable, Callable, Iterator, Union
from langchain.callbacks.base import AsyncCallbackManager, AsyncCallbackHandler
from fastapi.responses import StreamingResponse
from starlette.types import Send
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel
from textGenerators.OpenAITextGenerator import OpenAITextGenerator
from typing import List, Optional, Dict, Any, Union
from pydanticValidation.general_schemas import MediaModel

logger = logconfig.logger

router = APIRouter()

##############################
# CHAT STREAM
# https://gist.github.com/ninely/88485b2e265d852d3feb8bd115065b1a


@router.post("/chat_stream")
def stream(body: MediaModel):
    testData = body.userSettings['general']['returnTestData']
    if testData:
        return "Streaming. Test data!"
    logger.info("Processing chat_stream!")
    logger.info("body: %s" % body)
    #category = "chat"
    generator = get_generator(body.category, body.userSettings[body.category])
    try:
        return generator.stream_response(body)
    except Exception as e:
        logger.error("Error processing chat_stream: " + str(e))
        traceback.print_exc()
        return {"code": 400, "success": False, "message": "Error processing chat_stream: " + str(e)}

##############################
# CHAT OTHERS
# this will be used when recording is done in chat mode... and we need to send blob with audio to be processed
# we cannot use generate_asset - as we are not sending json, but we're sending form-data, so unforunately different code is needed
@router.post("/chat_audio2text")
async def chat_audio2text(
        action: str = Form(...),
        category: str = Form(...),
        userInput: str = Form(...),
        userSettings: str = Form(...),
        customerId: int = Form(...),
        audio: UploadFile = File(...),
        token = Depends(auth_user_token)
    ):
    logger.info("Processing recording!")
    # print all parameters' values in one logger.info statement
    logger.info("action: %s , category: %s, userInput: %s, userSettings: %s, customerId: %s, audio: %s" % (action, category, userInput, userSettings, customerId, audio))

    userInput = json.loads(userInput)
    userInput['audio'] = audio
    userSettings = json.loads(userSettings)
    generator = get_generator(category, userSettings[category])
    if generator == None:
        return {"code": 400, "success": False, "message": "No speech generator found"}

    response = await generator.process_job_request(action, userInput, [], customerId, 1)
    # this already consist of code, success, message
    return response

# THIS ONE IS NOT IN USE ATM
@router.post("/chat_text2audio")
async def chat_text2audio(job_request: MediaModel, token = Depends(auth_user_token)):
    logger.info("Processing chat_text2audio!")
    try:
        generator = get_generator(job_request.category, job_request.userSettings[job_request.category])
        if generator == None:
            return {"code": 400, "success": False, "message": "No speech generator found"}

        response = await generator.process_job_request(job_request.action, job_request.userInput, [], job_request.customerId, 1, job_request.userSettings)
        logger.info("RESPONSE: " + str(response))
        return response
    except Exception as e:
        logger.error("Error processing chat_text2audio: " + str(e))
        return {"code": 400, "success": False, "message": "Error processing chat_text2audio: " + str(e)}
