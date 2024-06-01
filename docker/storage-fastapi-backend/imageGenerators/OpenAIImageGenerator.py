from fastapi import HTTPException
import requests, os, base64
from fastapi.responses import JSONResponse
import traceback, json
import logconfig
from openai import OpenAI
logger = logconfig.logger

class OpenAIImageGenerator:
  def __init__(self):
    self.number_of_images = 1
    self.model = "dall-e-3"
    self.size_of_image = 1024
    self.quality = "standard" # hd
    #https://platform.openai.com/docs/guides/images/usage
    # adding: I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:
    # result: revised_prompt
    self.disable_safe_prompt_adjust = False
    self.client = OpenAI()

  def set_settings(self, userSettings={}):
    if userSettings:
        user_settings = userSettings.get("image", {})
        logger.debug("Setting user_settings: %s", user_settings)

        if "number_of_images" in user_settings:
            self.number_of_images = user_settings["number_of_images"]

        if "model" in user_settings:
            self.model = user_settings["model"]

        if "size_of_image" in user_settings:
            self.size_of_image = user_settings["size_of_image"]
            if user_settings["size_of_image"] < 1024:
                self.size_of_image = 1024

        if "quality" in user_settings:
            self.quality = user_settings["quality"]

        if "disable_safe_prompt_adjust" in user_settings:
            self.disable_safe_prompt_adjust = user_settings["disable_safe_prompt_adjust"]

  async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
    # OPTIONS
    self.set_settings(userSettings)

    try:
        if action == "generate":
            return await self.generate(userInput, assetInput, customerId, userSettings)
        else:
            return { "success": False, "message": "Unknown action", "code": 400 }
    except Exception as e:
        logger.error("Error processing image request: %s", str(e))
        raise HTTPException(status_code=500, detail="Error processing image request")

  async def generate(self, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False):
    try:
        #prompt = userInput.get('prompt') if userInput.get('prompt') else ""
        prompt = "beautiful album cover"
        if self.disable_safe_prompt_adjust:
            prompt = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS: " + prompt

        #returnTestData = True
        if returnTestData:
            # simulated response from SD
            response = {
                "created": 1681791159,
                "data": [
                    {
                        "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-xl9LUlwDaE7xHfomiY1yp9sG/user-qUElxkpAQyQkRERvyK5hqv4q/img-CpTOH90fLToA9M2E8HZoIh3a.png?st=2023-04-18T03%3A12%3A39Z&se=2023-04-18T05%3A12%3A39Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-18T00%3A27%3A24Z&ske=2023-04-19T00%3A27%3A24Z&sks=b&skv=2021-08-06&sig=k5%2B5n1gXzrkjC1TEy%2BSs8WAWSbbiAdoFTwjK/%2BW7jGI%3D"
                    }, {
                        "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-xl9LUlwDaE7xHfomiY1yp9sG/user-qUElxkpAQyQkRERvyK5hqv4q/img-2luwqtiKMGKfBR6rLL1Cx1vq.png?st=2023-04-17T16%3A20%3A31Z&se=2023-04-17T18%3A20%3A31Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-17T17%3A06%3A07Z&ske=2023-04-18T17%3A06%3A07Z&sks=b&skv=2021-08-06&sig=77b/MpFrhtrZlV6kC1UVyWlkgwBsTudPQPVZMiWyYAM%3D"
                    }
                ]
            }
        else:
            response = self.client.images.generate(
                prompt=prompt,
                n=self.number_of_images,
                size=str(self.size_of_image)+"x"+str(self.size_of_image),
                quality=self.quality,
                model=self.model,
                )

        logger.info("OAI generate_image response: " + str(response))
        # transform to json
        #image_url = response.data[0].url
        logger.info("REVISED PROMPT:")
        logger.info(response.data[0].revised_prompt)
        logger.info(response.data[0].url)
        finalUrl = response.data[0].url

        logger.debug("OAI generate_image response: " + str(response))

        return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": finalUrl}}, status_code=200)

    except Exception as e:
        logger.error("Error in generate_image (class)")
        logger.error(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=e) from e
