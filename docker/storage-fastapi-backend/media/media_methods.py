from fastapi.responses import JSONResponse
from fastapi import HTTPException
from datetime import datetime
from pydanticValidation.general_schemas import MediaModel
import traceback
import config as config
import logconfig
logger = logconfig.logger

async def media_methods(job_request: MediaModel, media_generator):
    if media_generator is None:
        logger.error("media_generator is None")
        return JSONResponse(content={"success": False, "message": "media_generator is None"}, status_code=500, media_type="application/json")
    try:
        time_start = datetime.now()

        logger.debug("media_methods triggered")
        logger.debug("media_method job_request" + str(job_request))

        if job_request.action in ["generate", "transcribe", "translate", "chat"]:
            response = await media_generator.process_job_request(
                action=job_request.action,
                userInput=job_request.userInput,
                assetInput=job_request.assetInput,
                customerId=job_request.customerId,
                userSettings=job_request.userSettings,
            )
            logger.debug("media_methods response: " + str(response))
        else:
            return JSONResponse(content={"success": False, "code": 404, "message": "Invalid job type"}, status_code=404, media_type="application/json")

        logger.debug(response)
        if response['code'] != 200:
            logger.error("Error in media!")
            return JSONResponse(content={"code": 500, "success": False, "message": response['message']}, status_code=500, media_type="application/json")

        respForResult = response['message'].get('result')

        # if completed we want to send to S3
        if response['message'].get('status') == "completed":
            # if its chat (chat for text - meaning we want to register it in DB) - it's not handled through brain.py - so we need to register request
            if job_request.action == "chat":
                #num_messages = len(job_request.assetInput)
                sessionId = job_request.userInput.get('sessionId')
                new_session_value = True if sessionId == None or sessionId == "" else False
                #new_session_value = True
                logger.info("!xx"*100)
                logger.info("respForResult: " + str(response['message'].get('content')))
                # calling store procedure
                url = node_api_endpoint + "/" + "newMessageInChat"
                body = {
                    "customerId": job_request.customerId,
                    "category": job_request.category,
                    "action": job_request.action,
                    "userInput": job_request.userInput,
                    "assetInput": job_request.assetInput,
                    "userSettings": job_request.userSettings,
                    "newSession": new_session_value,
                }
                logger.debug(body)

                responseRequest = requests.post(url, json=body,
                                         headers={ 'x-access-token': config.defaults['SSM_JWT_TOKEN']})
                logger.debug("responseRequest: " + str(responseRequest.json()))
                job_request.requestId = responseRequest.json()['message']['newRequestId']
                job_request.sessionId = responseRequest.json()['message']['sessionId']
            # there are 2 cases... one is ready_file - meaning that external API just generated final file
            # and second is job_id_to_check - meaning that external API just generated job_id and we need to check status
            if response['message']['result_type'] == "ready_file":
                parentRequestId = 0
                # for cases when in chat we generate images and audio and others (replicate) - we want to record parent request Id
                if job_request.action == "chat" and ( job_request.category == "image" or job_request.category == "audio" or job_request.category == "replicate" ):
                    parentRequestId = job_request.userInput.get('textRequestId')
                    logger.debug("parentRequestId: " + str(parentRequestId))

                # we send temporary file into cloud storage
                respStorage = await putFilesInStorage(job_request.customerId, respForResult, job_request.requestId, job_request.action, job_request.category, parentRequestId)
                logger.info(respStorage)
                respForResult = respStorage['message']
                if respStorage['code'] != 200:
                    logger.error("Error in putFilesInStorage")
                    return JSONResponse(content={"code": 500, "success": False, "message": respForResult}, status_code=500, media_type="application/json")

            # special rules for chat - because we want to keep chat session - and record all messages for single chat
            if job_request.action == "chat":
                # this is chat text response - so we want to send back not file location, but its content
                # later i will do stream hopefully - so this will go away
                if job_request.category == "text":
                    respForResult = response['message']['content']
                # here we also return request id - idea is that for example we generate text and then audio from this text
                # so for DB entry of audio we want to record request id of text generation (so later in UI its easy to get it)
                respForResult = { "result": respForResult, "sessionId": job_request.sessionId, "requestId": job_request.requestId }

        # we set message to S3 URL
        finalResponse = {"code": 200, "success": True,
                        "message": {
                            "status": response['message'].get('status'),
                            "result_type": response['message']['result_type'], 
                            "result": respForResult
                            }
                        }

        time_finish = datetime.now()
        time_diff = (time_finish - time_start).total_seconds()
        logger.info(f"Execution time: {time_diff}")
        logger.info("Final response: " + str(finalResponse))

        return JSONResponse(content=finalResponse, status_code=200)
    except HTTPException as e:
        print(e.detail)
        return JSONResponse(content={"success": False, "code": e.status_code, "message": e.detail}, status_code=e.status_code, media_type="application/json")
    except Exception as e:
        print(e)
        logger.error("Error in generate_media")
        traceback.print_exc()
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500, media_type="application/json")
