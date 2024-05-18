from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

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
    message = f"Hello world! From FastAPI running on Uvicorn with Gunicorn. Using Python {version}"
    # return {'status_code': 200, 'success': True, "message": message }
    return JSONResponse(content={'status_code': 200, 'success': True, "message": message}, media_type="application/json")

@app.post("/chatold")
async def chat(job_request: MediaModel):
    logger.info("*"*20)
    logger.info(job_request.userInput)
    mygen = get_generator(job_request.action, { "generator": job_request.userSettings["generator"]})
    abc = await mygen.process_job_request(job_request.action, { "input": job_request.userInput['prompt']}, {}, userSettings=job_request.userSettings)
    #logger.info(abc)
    return JSONResponse(content={'status_code': 200, 'success': True, "message": abc}, media_type="application/json")

@app.post("/chat")
async def chat(job_request: MediaModel):
    logger.info("*"*20)
    logger.info(job_request.userInput)
    logger.info(job_request)
    my_generator = get_generator(job_request.category, job_request.userSettings[job_request.category])
    if my_generator is None:
        return JSONResponse(content={'status_code': 400, 'success': False, "message": "Problem with your getting proper generator. Verify your settings"}, media_type="application/json")

    return StreamingResponse(my_generator.process_job_request(job_request), media_type="text/event-stream")

import time
def generate_data():

    for i in range(1, 3):
        yield f"data: {str(i)}\n\n"
        logger.info("!!!")
        logger.info(str(i))
        time.sleep(0.5)  # Simulate delay
    yield "data: END\n\n"

@app.post("/chatstream2")
async def stream(job_request: MediaModel):
    return StreamingResponse(generate_data(), media_type="text/event-stream")

