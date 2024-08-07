from fastapi import FastAPI, Request, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import traceback
import logconfig
import json
import sys

from pydanticValidation.general_schemas import MediaModel
from main_generators import startup_event_generators, get_generator, get_garmin_provider
from main_auth_token import auth_user_token
import config as config

logger = logconfig.logger

logger.info("!!!!!!")
logger.info(config.defaults['environment'])
logger.info(config.defaults['MYSQL_HOST'])

#################
version = f"{sys.version_info.major}.{sys.version_info.minor}"

# to set up generators on startup_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    await startup_event_generators(app)
    yield

app = FastAPI(lifespan=lifespan, debug=True)

# prod CORS is done via web server
if config.defaults['environment'] != 'production':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

##############################
# GENERAL generate functions (that do not need file upload or streaming)
@app.post("/generate")
async def generate_asset(job_request: MediaModel, token=Depends(auth_user_token)):
    logger.info("!" * 100)
    logger.info("Job request: " + str(job_request))
    try:
        if job_request.category in ["tts", "text", "image"]:
            my_generator = get_generator(
                job_request.category, job_request.userSettings[job_request.category])
            if my_generator is None:
                return JSONResponse(content={'status_code': 400, 'success': False, "message": "Problem with your getting proper generator. Verify your settings"}, media_type="application/json")

            response = await my_generator.process_job_request(job_request.action, job_request.userInput, job_request.assetInput, job_request.customerId, userSettings=job_request.userSettings)

            # special case for tts streaming (as diff response needed)
            if job_request.category == "tts" and job_request.action == "tts_stream":
                return StreamingResponse(response, media_type="audio/pcm")

            response_content = response.body.decode(
                "utf-8") if isinstance(response, JSONResponse) else response
            logger.info("ALL OK")
            logger.info(response_content)
            return JSONResponse(content=json.loads(response_content), status_code=response.status_code, media_type="application/json")
        else:
            return JSONResponse(content={'status_code': 400, 'success': False, "message": "Unknown category"}, media_type="application/json")
    except HTTPException as e:
        logger.info("ERROR: %s" % e)
        return JSONResponse(status_code=e.status_code, content={"code": e.status_code, "success": False, "message": {"status": "fail", "result": str(e)}})
    except Exception as e:
        logger.error("Error while processing request")
        logger.error(e)
        traceback.print_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"code": 500, "success": False, "message": {"status": "fail", "result": str(e)}})


##############################
# CHAT STREAMING (although used also for non streaming because it is possible)
@app.post("/chat")
async def chat(job_request: MediaModel, token=Depends(auth_user_token)):
    logger.info("*" * 100)
    logger.info(job_request)

    my_generator = get_generator(
        job_request.category, job_request.userSettings[job_request.category])
    if my_generator is None:
        return JSONResponse(content={'code': 400, 'success': False, "message": {"status": "fail", "result": 'Problem with getting proper generator. Verify your settings'}}, status_code=400)

    try:
        stream = await my_generator.process_job_request(job_request.action, job_request.userInput, job_request.assetInput, userSettings=job_request.userSettings)
        return StreamingResponse(stream, media_type="text/event-stream")
    except Exception as e:
        logger.error("Error processing job request: %s", str(e))
        return JSONResponse(content={'code': 500, 'success': False, "message": {"status": "fail", "result": str(e)}}, status_code=500)

##############################
# this will be used when recording is done in chat mode... and we need to send blob with audio to be processed
# we cannot use generate_asset - as we are not sending json, but we're sending form-data, so unfortunately different code is needed
@app.post("/chat_audio2text")
async def chat_audio2text(
    action: str = Form(...),
    category: str = Form(...),
    userInput: str = Form(...),
    userSettings: str = Form(...),
    customerId: int = Form(...),
    file: UploadFile = File(...),
    token=Depends(auth_user_token)
):
    try:
        logger.info("Processing recording!")
        logger.info("action: %s , category: %s, userInput: %s, userSettings: %s, customerId: %s, audio: %s" %
                    (action, category, userInput, userSettings, customerId, file.filename))

        userInput = json.loads(userInput)
        userInput['file'] = file
        userSettings = json.loads(userSettings)
        generator = get_generator(category, userSettings[category])

        if generator is None:
            raise HTTPException(
                status_code=400, detail="No speech generator found")

        response = await generator.process_job_request(action, userInput, [], customerId, userSettings)
        response_content = response.body.decode(
            "utf-8") if isinstance(response, JSONResponse) else response

        logger.info(response_content)
        return JSONResponse(content=json.loads(response_content), status_code=response.status_code, media_type="application/json")
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"code": e.status_code, "success": False, "message": {"status": "fail", "result": str(e)}})
    except Exception as e:
        logger.error("Error while processing request")
        logger.error(e)
        traceback.print_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"code": 500, "success": False, "message": {"status": "fail", "result": str(e)}})


###########################################
  ### SECTIONS FOR INTERNAL METHODS ####
########### AWS ###########################

# Endpoint to handle AWS stuff (as of now only file upload and send to S3)
@app.post("/api/aws")
async def aws_methods(
    action: str = Form(...),
    category: str = Form(...),
    userInput: str = Form(...),
    userSettings: str = Form(...),
    customerId: int = Form(...),
    file: UploadFile = File(...),
    token=Depends(auth_user_token)
):
    try:
        logger.info("Processing file upload!")
        logger.info("action: %s , category: %s, userInput: %s, userSettings: %s, customerId: %s, file: %s" %
                    (action, category, userInput, userSettings, customerId, file.filename))

        userInput = json.loads(userInput)
        userInput['file'] = file
        userSettings = json.loads(userSettings)
        generator = get_generator(category, "doesntmatter")

        if generator is None:
            raise HTTPException(
                status_code=400, detail="No aws generator found")

        response = await generator.process_job_request(action, userInput, [], customerId, userSettings)

        response_content = response.body.decode(
            "utf-8") if isinstance(response, JSONResponse) else response

        logger.info(response_content)
        return JSONResponse(content=json.loads(response_content), status_code=response.status_code, media_type="application/json")

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"code": e.status_code, "success": False, "message": {"status": "fail", "result": str(e)}})
    except Exception as e:
        logger.error("Error while processing request")
        logger.error(e)
        traceback.print_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"code": 500, "success": False, "message": {"status": "fail", "result": str(e)}})

########### DB ###########################
# Endpoint to handle DB stuff (getting, inserting, etc data to mysql)
@app.post("/api/db")
async def db_methods(job_request: MediaModel, request: Request):  # token below
    # endpoint without auth - for example user login - because he doesnt have token yet
    if job_request.action not in ['db_auth_user']:
        token = await auth_user_token(request)

    logger.info("*" * 100)
    logger.info(job_request)

    try:
        my_generator = get_generator(job_request.category, "doesntmatter")
        if my_generator is None:
            return JSONResponse(content={'status_code': 400, 'success': False, "message": "Problem with your getting proper generator. Verify your settings"}, media_type="application/json")

        response = await my_generator.process_job_request(job_request.action, job_request.userInput, job_request.assetInput, job_request.customerId, userSettings=job_request.userSettings)

        response_content = response.body.decode(
            "utf-8") if isinstance(response, JSONResponse) else response
        # there is so much data in those methods - that it just doesnt make sense to log it all
        if job_request.action != 'db_get_user_session' and job_request.action != 'db_search_messages' and job_request.action != 'db_all_sessions_for_user':
            logger.debug(response_content)
        return JSONResponse(content=json.loads(response_content), status_code=response.status_code, media_type="application/json")

    except HTTPException as e:
        logger.error("ALL NOT 1 OK")
        logger.error(e)
        return JSONResponse(status_code=e.status_code, content={"code": e.status_code, "success": False, "message": {"status": "fail", "result": str(e)}})
        # raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        logger.info("ALL NOT 2 OK")
        logger.error("Error while processing request")
        logger.error(e)
        traceback.print_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"code": 500, "success": False, "message": {"status": "fail", "result": str(e)}})


########### GARMIN ###########################
@app.post("/api/garmin")
async def generate_asset(job_request: MediaModel, token=Depends(auth_user_token)):
    logger.info("*" * 100)
    logger.info(job_request)
    try:
        garmin_provider = get_garmin_provider(app)
        response = await garmin_provider.process_job_request(job_request.action, job_request.userInput, job_request.assetInput, job_request.customerId, userSettings=job_request.userSettings)

        response_content = response.body.decode(
            "utf-8") if isinstance(response, JSONResponse) else response

        logger.debug(response_content)
        return JSONResponse(content=json.loads(response_content), status_code=response.status_code, media_type="application/json")

    except HTTPException as e:
        logger.info("ERROR: %s" % e)
        return JSONResponse(status_code=e.status_code, content={"code": e.status_code, "success": False, "message": {"status": "fail", "result": str(e)}})
    except Exception as e:
        logger.error("Error while processing request")
        logger.error(e)
        traceback.print_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"code": 500, "success": False, "message": {"status": "fail", "result": str(e)}})
