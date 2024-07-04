"""Thanks to author of https://github.com/cyberjunky/python-garminconnect"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
import garth
import config
import traceback

import logconfig
import config as config

# import test data
from garmin.garmin_test_data import TEST_DATA

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
            self.use_test_data = user_settings["general"]["returnTestData"]
            user_settings = user_settings.get("provider.garmin", {})

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
                return await self.get_sleep_data(userInput)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing Garmin request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing Garmin request")

    async def get_sleep_data(self, userInput: dict):
        if self.use_test_data:
            response = TEST_DATA["get_sleep_data"]
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        # date in format 2024-06-08
        print("userInput: ", userInput)
        date = userInput.get('date', None)

        if not date:
            raise HTTPException(
                status_code=400, detail="Date is required for get_sleep_data")
        try:
            url = f"/wellness-service/wellness/dailySleepData/{self.display_name}"
            params = {"date": str(date), "nonSleepBufferMinutes": 60}
            # login = self.login()
            # print(login)
            response = self.call_api(url, params=params)
            # response = "OK"
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in db_new_session: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error in garmin. get_sleep_data")
