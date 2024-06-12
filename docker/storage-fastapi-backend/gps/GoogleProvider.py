from fastapi import HTTPException
from fastapi.responses import JSONResponse
import config

import logconfig

logger = logconfig.logger

logger = logconfig.logger


class googleProvider:
    def __init__(self):
        self.aws_region = "eu-west-1"  # not in use

    def set_settings(self, user_settings={}):
        if user_settings:
            # and now process aws settings (doubt it will be used)
            # this is not in use - just for maybe future
            user_settings = user_settings.get("aws", {})
            # Update model name
            if "aws_region" in user_settings:
                user_settings["aws_region"] = user_settings["aws_region"]

    async def process_job_request(
        self,
        action: str,
        userInput: dict,
        assetInput: dict,
        customerId: int = None,
        userSettings: dict = {},
    ):
        # OPTIONS
        self.set_settings(userSettings)
        try:
            if action == "s3_upload":
                return await self.s3_upload(action, userInput, assetInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing AWS request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing AWS request")
