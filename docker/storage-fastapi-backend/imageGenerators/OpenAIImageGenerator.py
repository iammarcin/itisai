from fastapi import HTTPException
import requests
from fastapi.responses import JSONResponse
from aws.awsProvider import awsProvider
import traceback
import json
import logconfig
from openai import OpenAI, BadRequestError
from tempfile import NamedTemporaryFile
from pathlib import Path

logger = logconfig.logger

# little helper class - s3 upload in aws provider was already set and used by other functions
# and it needs file and filename to process the file


class FileWithFilename:
    def __init__(self, file, filename):
        self.file = file
        self.filename = filename


class OpenAIImageGenerator:
    def __init__(self):
        self.number_of_images = 1
        self.model = "dall-e-3"
        self.size_of_image = 1024
        self.quality = "standard"  # hd
        # https://platform.openai.com/docs/guides/images/usage
        # adding: I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:
        # result: revised_prompt
        self.disable_safe_prompt_adjust = False
        self.use_test_data = False
        self.client = OpenAI()

    def set_settings(self, user_settings={}):
        if user_settings:
            # if we want to return test data
            self.use_test_data = user_settings["general"]["returnTestData"]

            user_settings = user_settings.get("image", {})
            logger.debug("Setting user_settings: %s", user_settings)

            if "number_of_images" in user_settings:
                self.number_of_images = user_settings["number_of_images"]

            if "model" in user_settings:
                self.model = user_settings["model"]

            if "size_of_image" in user_settings:
                self.size_of_image = user_settings["size_of_image"]
                if user_settings["size_of_image"] < 1024:
                    self.size_of_image = 1024

            if "quality_hd" in user_settings:
                if user_settings["quality_hd"]:
                    self.quality = "hd"
                else:
                    self.quality = "standard"

            if "disable_safe_prompt_adjust" in user_settings:
                self.disable_safe_prompt_adjust = user_settings["disable_safe_prompt_adjust"]

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)

        try:
            if action == "generate":
                return await self.generate(userInput, assetInput, customerId, userSettings)
            else:
                return {"success": False, "message": "Unknown action", "code": 400}
        except Exception as e:
            logger.error("Error processing image request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing image request")

    async def generate(self, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}):
        try:
            if userInput.get('text') is None:
                raise HTTPException(
                    status_code=400, detail="Prompt is required")

            prompt = userInput.get('text')
            # prompt = "beautiful album cover"
            if self.disable_safe_prompt_adjust:
                prompt = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS: " + prompt

            if self.use_test_data:
                finalUrl = 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-xl9LUlwDaE7xHfomiY1yp9sG/user-qUElxkpAQyQkRERvyK5hqv4q/img-4DdoHjcSqIQVSLJU7ijWrCw2.png?st=2024-06-30T03%3A46%3A59Z&se=2024-06-30T05%3A46%3A59Z&sp=r&sv=2023-11-03&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-06-30T01%3A52%3A50Z&ske=2024-07-01T01%3A52%3A50Z&sks=b&skv=2023-11-03&sig=1PbGkkHGY9%2BGuyqvtnNe02GQ7F%2Blgcjk8mqqniPfTRw%3D'
                finalUrl = await self.saveFileAndSendToS3(finalUrl, customerId)
                return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": finalUrl}}, status_code=200)
            else:
                logger.info("Image gen start!")
                response = self.client.images.generate(
                    prompt=prompt,
                    n=self.number_of_images,
                    size=str(self.size_of_image)+"x"+str(self.size_of_image),
                    quality=self.quality,
                    model=self.model,
                )

            logger.debug("OAI generate_image response: " + str(response))
            # transform to json
            # image_url = response.data[0].url
            logger.info("REVISED PROMPT:")
            logger.info(response.data[0].revised_prompt)
            logger.info(response.data[0].url)
            openaiUrl = response.data[0].url

            # Save the image from the finalUrl to a temporary file
            finalUrl = await self.saveFileAndSendToS3(openaiUrl, customerId)

            logger.debug("OAI generate_image response: " + str(response))

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": finalUrl}}, status_code=200)

        except BadRequestError as e:
            logger.error("Error in generate_image (class)")
            logger.error(e)
            traceback.print_exc()
            error_message = e.error.get('message', 'Unknown error')
            error_code = e.error.get('code', 'unknown_error')
            if error_code == 'content_policy_violation':
                return JSONResponse(content={"success": False, "code": 400, "message": {"status": "rejected", "result": error_message}}, status_code=400)
            raise HTTPException(status_code=500, detail=str(e)) from e
        except Exception as e:
            logger.error("Error in generate_image (class)")
            logger.error(e)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=e) from e

    async def saveFileAndSendToS3(self, openaiUrl: str, customerId: int):
        try:
            with NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                image_response = requests.get(openaiUrl)
                if image_response.status_code == 200:
                    tmp_file.write(image_response.content)
                    tmp_file_path = tmp_file.name
                else:
                    raise HTTPException(
                        status_code=500, detail="Failed to download image")

            with open(tmp_file_path, "rb") as tmp_file:
                file_with_filename = FileWithFilename(
                    tmp_file, Path(tmp_file_path).name)
                s3_response = await awsProvider.s3_upload(
                    awsProvider,
                    action="s3_upload",
                    userInput={"file": file_with_filename},
                    assetInput={},
                    customerId=customerId
                )

                s3_response_content = json.loads(
                    s3_response.body.decode("utf-8"))
                logger.info("s3_response_content %s", s3_response_content)
                s3_url = s3_response_content["message"]["result"]
                return s3_url

        except Exception as e:
            logger.error("Error in saveFileAndSendToS3 (class)")
            logger.error(e)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=e) from e
