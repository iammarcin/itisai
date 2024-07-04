"""Thanks to author of https://github.com/cyberjunky/python-garminconnect"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
import garth
import config
import traceback

import logconfig
import config as config

logger = logconfig.logger

DEBUG = config.defaults["DEBUG"]
VERBOSE_SUPERB = config.defaults["VERBOSE_SUPERB"]


class garminProvider:
    def __init__(self):
        self.garmin_home = "~/.garmin_session"
        self.garth = garth.Client()
        self.display_name = None
        self.full_name = None
        self.unit_system = None

    def set_settings(self, user_settings={}):
        if user_settings:
            # and now process aws settings (doubt it will be used)
            # this is not in use - just for maybe future
            user_settings = user_settings.get("aws", {})
            # Update model name
            if "aws_region" in user_settings:
                self.aws_region = user_settings["aws_region"]

    def call_api(self, path, **kwargs):
        return self.garth.connectapi(path, **kwargs)

    def login(self):
        try:
            self.garth.load(self.garmin_home)
        except Exception as e:
            logger.info(f"Garmin Connect auth failed. {e}")
            return False

        self.display_name = self.garth.profile["displayName"]
        self.full_name = self.garth.profile["fullName"]

        settings = self.call_api(
            "/userprofile-service/userprofile/user-settings")

        self.unit_system = settings["userData"]["measurementSystem"]
        logger.debug(f"Logged in as {self.display_name} ({self.full_name})")
        logger.debug(f"Unit system: {self.unit_system}")

        return True

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)

        try:
            if action == "get_sleep_data":
                return await self.get_sleep_data(userInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing DB request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing DB request")

    async def get_sleep_data(self, userInput: dict, customerId: int):
        date = userInput.get(date)
        try:
            url = f"/wellness-service/wellness/dailySleepData/{self.display_name}"
            params = {"date": str(date), "nonSleepBufferMinutes": 60}

            response = self.call_api(url, params=params)
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in db_new_session: %s", str(e))
            traceback.print_exc()
            # return JSONResponse(content={"False": True, "code": 400, "message": {"status": "fail", "result": str(e)}}, status_code=400)
            raise HTTPException(
                status_code=500, detail="Error in DB! db_new_session")
