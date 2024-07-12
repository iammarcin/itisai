from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import HTTPException
from pathlib import Path
from openai import OpenAI
from aws.awsProvider import awsProvider
import logconfig
import os
import json
import config as config
from tempfile import NamedTemporaryFile


logger = logconfig.logger

# little helper class - s3 upload in aws provider was already set and used by other functions
# and it needs file and filename to process the file
class FileWithFilename:
    def __init__(self, file, filename):
        self.file = file
        self.filename = filename


class OpenAITTSGenerator:
    def __init__(self):
        self.model_name = "tts-1"
        self.voice = "alloy"
        self.format = "pcm"
        self.streaming = False
        self.speed = 1
        self.client = OpenAI()

    def set_settings(self, user_settings={}):
        if user_settings:
            # and now process aws settings (doubt it will be used)
            # this is not in use - just for maybe future
            user_settings = user_settings.get("tts", {})
            if "model" in user_settings:
                self.model_name = user_settings["model"]

            if "voice" in user_settings:
                self.voice = user_settings["voice"]

            if "format" in user_settings:
                self.format = user_settings["format"]

            if "streaming" in user_settings:
                self.streaming = user_settings["streaming"]

            if "speed" in user_settings:
                self.speed = user_settings["speed"]

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)
        try:
            if action == "tts_no_stream":
                return await self.generate_tts(userInput, customerId)
            elif action == "tts_stream":
                return self.stream_tts(userInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing TTS request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing TTS request")

    async def generate_tts(self, userInput: dict, customerId: int = 1):
        try:
            text = userInput["text"]

            # fail on purpose
            # test = userInput['test']

            response = self.client.audio.speech.create(
                model=self.model_name,
                voice=self.voice,
                speed=self.speed,
                response_format=self.format,
                input=text,
            )

            with NamedTemporaryFile(delete=False, suffix=f".{self.format}") as tmp_file:
                tmp_file_path = tmp_file.name
                response.stream_to_file(tmp_file_path)

            with open(tmp_file_path, "rb") as tmp_file:
                file_with_filename = FileWithFilename(
                    tmp_file, Path(tmp_file_path).name)
                logger.info("Uploading TTS to S3")
                logger.info(file_with_filename)
                s3_response = await awsProvider.s3_upload(
                    awsProvider,
                    action="s3_upload",
                    userInput={"file": file_with_filename},
                    assetInput={},
                    customerId=customerId
                )

            s3_response_content = json.loads(s3_response.body.decode("utf-8"))
            logger.info("s3_response_content %s", s3_response_content)
            s3_url = s3_response_content["message"]["result"]

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": s3_url}}, status_code=200)
        except Exception as e:
            logger.error("Error generating TTS: %s", str(e))
            raise HTTPException(status_code=500, detail="Error generating TTS")

    def stream_tts(self, userInput: dict, customerId: int = 1):

        text = userInput["text"]
        self.format = "opus"

        try:
            with self.client.audio.speech.with_streaming_response.create(
                model=self.model_name,
                voice=self.voice,
                response_format=self.format,
                speed=self.speed,
                input=text,
            ) as response:
                logger.info("-" * 33)
                for chunk in response.iter_bytes(1024):
                    logger.debug(chunk)
                    yield chunk

            # return StreamingResponse(iter_audio_stream(), media_type="audio/mpeg", headers={"Transfer-Encoding": "chunked"})
        except Exception as e:
            logger.error("Error streaming TTS: %s", str(e))
            raise HTTPException(status_code=500, detail="Error streaming TTS")

    def _generate_mp3_headers(self):
        # Generate MP3 headers if required
        headers = b""
        # Append any necessary MP3 headers here
        yield headers
