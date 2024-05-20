from fastapi import FastAPI, Request, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from media.media_methods import *

from prompts.text import getTextPromptTemplate

import traceback
import logconfig
import json
import sys
#from main_chat_methods import router as chat_router
from pydanticValidation.general_schemas import MediaModel #, GenerateAssetOrSuggestion, ProcessWebUrl, ProcessYTSubmit
#from pydanticValidation.video_schemas import *
from main_generators import startup_event_generators, get_generator
import config as config

logger = logconfig.logger

#################

version = f"{sys.version_info.major}.{sys.version_info.minor}"

# to set up generators on startup_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    await startup_event_generators(app)
    yield
    # You can add shutdown events after yield if needed

app = FastAPI(lifespan=lifespan, debug=True)

# middleware for catching problems with pydantic data validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.info("Error validating request data")
    logger.info(exc.errors())

    return JSONResponse(
        status_code=422,
        content={'code': 422, 'success': False,
                 'message': "Error validating data %s " % exc.errors()},
    )

@app.get("/monitorback")
async def read_root():
    message = f"Hello world! I work fine!"
    # return {'status_code': 200, 'success': True, "message": message }
    return JSONResponse(content={'status_code': 200, 'success': True, "message": message}, media_type="application/json")

@app.post("/generate")
async def generate_asset(job_request: MediaModel): #, token = Depends(auth_user_token)):
    logger.info("!"*100)
    logger.info("generating data. returnTestData Mode: " + str(job_request.userSettings["general"].get("returnTestData", False)))
    logger.info("Job request: " + str(job_request))

    if job_request.category == "speech":
        logger.info("*"*20)
        logger.info(job_request.userInput)
        logger.info(job_request)
        my_generator = get_generator(job_request.category, job_request.userSettings[job_request.category])
        if my_generator is None:
            return JSONResponse(content={'status_code': 400, 'success': False, "message": "Problem with your getting proper generator. Verify your settings"}, media_type="application/json")

        return JSONResponse(await my_generator.process_job_request(job_request.action, job_request.userInput, job_request.assetInput, userSettings=job_request.userSettings), media_type="application/json")

    if job_request.category == "text":
        logger.info("*"*20)
        logger.info(job_request.userInput)
        logger.info(job_request)
        my_generator = get_generator(job_request.category, job_request.userSettings[job_request.category])
        if my_generator is None:
            return JSONResponse(content={'status_code': 400, 'success': False, "message": "Problem with your getting proper generator. Verify your settings"}, media_type="application/json")

        result = await my_generator.process_job_request(job_request.action, job_request.userInput, job_request.assetInput, userSettings=job_request.userSettings)
        return JSONResponse(content=result, media_type="application/json")

    if job_request.category == "textOKKKKK" or job_request.category == "audio" or job_request.category == "image":# or job_request.category == "speech":
        try:
            generator = get_generator(job_request.category, job_request.userSettings[job_request.category])
            if generator == None:
                return {"code": 400, "success": False, "message": "No generator found"}

            response_data = await media_methods(job_request, generator)

            if response_data.status_code != 200:
                return {"code": response_data.status_code, "success": False, "message": f"Error while generating media. {response_data.content}"}

        except Exception as e:
            logger.error(e)
            traceback.print_exc()  # useful!
            return {"code": 400, "success": False, "error": f"Error while generating media ", "message": str(e)}

    else:
        return {"code": 400, "success": False, "error": "Invalid category"}

@app.post("/chat")
async def chat(job_request: MediaModel):
    logger.info("*" * 20)
    logger.info(job_request.userInput)
    logger.info(job_request)

    my_generator = get_generator(job_request.category, job_request.userSettings[job_request.category])
    if my_generator is None:
        return JSONResponse(content={'code': 400, 'success': False, 'message': 'Problem with getting proper generator. Verify your settings'}, status_code=400)

    try:
        stream = await my_generator.process_job_request(job_request.action, job_request.userInput, job_request.assetInput, userSettings=job_request.userSettings)
        return StreamingResponse(stream, media_type="text/event-stream")
    except Exception as e:
        logger.error("Error processing job request: %s", str(e))
        return JSONResponse(content={'code': 500, 'success': False, 'message': 'Internal server error'}, status_code=500)

##############################
# this will be used when recording is done in chat mode... and we need to send blob with audio to be processed
# we cannot use generate_asset - as we are not sending json, but we're sending form-data, so unforunately different code is needed
@app.post("/chat_audio2text")
async def chat_audio2text(
        action: str = Form(...),
        category: str = Form(...),
        userInput: str = Form(...),
        userSettings: str = Form(...),
        customerId: int = Form(...),
        audio: UploadFile = File(...),
        #token = Depends(auth_user_token)
    ):
    try:
        logger.info("Processing recording!")
        logger.info("action: %s , category: %s, userInput: %s, userSettings: %s, customerId: %s, audio: %s" % 
                    (action, category, userInput, userSettings, customerId, audio.filename))

        userInput = json.loads(userInput)
        userInput['audio'] = audio
        userSettings = json.loads(userSettings)
        generator = get_generator(category, userSettings[category])

        if generator is None:
            raise HTTPException(status_code=400, detail="No speech generator found")

        response = await generator.process_job_request(action, userInput, [], customerId, userSettings)
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"code": e.status_code, "success": False, "message": e.detail})
    except Exception as e:
        logger.error("Error while processing request")
        logger.error(e)
        traceback.print_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"code": 500, "success": False, "message": str(e)})

