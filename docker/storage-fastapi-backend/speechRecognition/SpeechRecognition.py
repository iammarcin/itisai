from helperUploadDownload import saveContentToFile
from openai import OpenAI
from groq import Groq
from fastapi import HTTPException
from fastapi.responses import JSONResponse

import logconfig
import traceback
logger = logconfig.logger


class SpeechRecognitionGenerator:
    def __init__(self):
        self.save_to_file = True
        self.save_to_file_iterator = 0
        self.model_name = "whisper-1"
        self.optional_prompt = ""
        # between 0 and 1, higher - more random, 0 - log prob increasing temperature automatically
        self.temperature = 0.2
        # vtt - with timestamps, i think text should be set as standard so later in save2file we have no problem
        self.response_format = "text"
        self.language = "en"
        self.client = OpenAI()

    def set_settings(self, user_settings={}):
        if user_settings:
            # if we want to return test data
            self.use_test_data = user_settings["general"].get(
                "returnTestData", False)

            # and now process speech settings
            user_settings = user_settings.get("speech", {})
            logger.debug("Setting user_settings: %s", user_settings)
            if "response_format" in user_settings:
                self.response_format = user_settings["response_format"]

            if "temperature" in user_settings:
                self.temperature = user_settings["temperature"]

            if "language" in user_settings:
                self.language = user_settings["language"]

            if "model" in user_settings:
                self.model_name = user_settings["model"]

            if "optional_prompt" in user_settings:
                self.optional_prompt = user_settings["optional_prompt"]

            if "use_groq" in user_settings:
                self.use_groq = user_settings["use_groq"]
                if self.use_groq:
                    self.client = Groq()
                    self.model_name = "whisper-large-v3"

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)
        try:
            if action == "transcribe" or action == "translate" or action == "chat":
                return await self.whisper(action, userInput, assetInput, customerId, userSettings)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing speech request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing speech request")

    async def whisper(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        logger.debug("SpeechGenerator whisper - start")

        if self.use_test_data:
            return {'code': 200, 'success': True, 'message': {"status": "completed", "result": "Hello! (TEST transcribed)"}}

        # fail on purpose
        # test = userInput['test']

        try:
            # only for chat - we have to save blob to file (as its coming from recorder from Chat in react)
            if action == "chat":
                upload_file = userInput.get('file')
                audio_file = await saveContentToFile(customerId, upload_file, 1)
                file = audio_file['message']
                audio_file = open(file, "rb")
            else:  # for rest we have file that we need to feed to whisper
                # TEMP TEST
                audio_file = open(
                    "/storage/testApi/20230419_391sa2_output_1.mp3", "rb")

            logger.info("Using model: %s", self.model_name)

            if action == "translate":
                response = self.client.audio.translations.create(
                    model=self.model_name,
                    file=audio_file,
                    prompt=self.optional_prompt,
                    response_format=self.response_format,
                    temperature=self.temperature)
            else:
                response = self.client.audio.transcriptions.create(
                    model=self.model_name,
                    file=audio_file,
                    prompt=self.optional_prompt,
                    response_format=self.response_format,
                    temperature=self.temperature,
                    language=self.language)

            response_text = response.text if hasattr(response, 'text') else response

            logger.debug("SpeechGenerator whisper - response: %s" % response_text)

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response_text}}, status_code=200)

        except HTTPException as e:
            logger.error(
                "Error while making speech API call to Speech - HTTPException ")
            logger.error(e)
            raise HTTPException(
                status_code=500, detail="Error generating speech")
        except Exception as e:
            logger.error(
                "Error while making speech API call to Speech - exception ")
            logger.error(e)
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error generating speech")
