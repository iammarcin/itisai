from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import HTTPException
from pathlib import Path
from openai import OpenAI
from aws.awsProvider import awsProvider
import logconfig, os, json
import config as config
from tempfile import NamedTemporaryFile


logger = logconfig.logger

class OpenAITTSGenerator:
    def __init__(self):
        self.model_name = "tts-1"
        self.voice = "alloy"
        self.format = "opus"
        self.streaming = False
        self.llm = OpenAI()

    def set_settings(self, user_settings={}):
        if user_settings:
            self.voice = user_settings.get("voice", "alloy")
            self.format = user_settings.get("format", "opus")
            self.streaming = user_settings.get("streaming", False)

    async def process_tts_request(self, text: str, userSettings: dict = {}):
        self.set_settings(userSettings)

        if self.streaming:
            return self.stream_tts(text)
        else:
            return await self.generate_tts(text)

    async def generate_tts(self, text: str):
        try:
            response = self.llm.audio.speech.create(
                model=self.model_name,
                voice=self.voice,
                input=text,
            )

            class FileWithFilename:
                def __init__(self, file, filename):
                    self.file = file
                    self.filename = filename

            file_path = Path(__file__).parent / "output.opus"
            response.stream_to_file(file_path)
            print("2")
            print(file_path)
            print(type(file_path))
            '''
            # Open the file and set the filename attribute for the BufferedReader object
            with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file_path = tmp_file.name
                for chunk in response.with_streaming_response():
                    tmp_file.write(chunk)

            with open(tmp_file_path, "wb") as f:
                for chunk in response.with_streaming_response():
                    f.write(chunk)
            '''
            with open(file_path, "rb") as tmp_file:
                file_with_filename = FileWithFilename(tmp_file, file_path.name)
                s3_response = await awsProvider.s3_upload(
                    awsProvider,
                    action="s3_upload",
                    userInput={"file": file_with_filename},
                    assetInput={},  # Add any required assetInput here
                    customerId=1  # Replace with appropriate customerId
                )

            s3_response_content = json.loads(s3_response.body.decode("utf-8"))
            s3_url = s3_response_content["message"]["result"]

            return JSONResponse(content={"message": "TTS generated successfully", "audio_url": s3_url}, status_code=200)
        except Exception as e:
            logger.error("Error generating TTS: %s", str(e))
            raise HTTPException(status_code=500, detail="Error generating TTS")

    def stream_tts(self, text: str):
        try:
            response = self.llm.audio.speech.create(
                model=self.model_name,
                voice=self.voice,
                input=text,
            )

            def iter_audio_stream():
                for chunk in response.with_streaming_response():
                    if chunk:
                        yield chunk

            return StreamingResponse(iter_audio_stream(), media_type="audio/mpeg", headers={"Transfer-Encoding": "chunked"})
        except Exception as e:
            logger.error("Error streaming TTS: %s", str(e))
            raise HTTPException(status_code=500, detail="Error streaming TTS")
