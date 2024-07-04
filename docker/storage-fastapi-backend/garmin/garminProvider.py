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

        # date in format 2024-06-08
        date = userInput.get('date', None)
        if not date:
            raise HTTPException(
                status_code=400, detail="Date is required for Garmin provider")

        try:
            if action == "get_sleep_data":
                return await self.get_sleep_data(userInput)
            elif action == "get_user_summary":
                return self.get_user_summary(userInput)
            elif action == "get_body_composition":
                return self.get_body_composition(userInput)
            elif action == "get_rhr_day":
                return self.get_rhr_day(userInput)
            elif action == "get_training_readiness":
                return self.get_training_readiness(userInput)
            elif action == "get_endurance_score":
                return self.get_endurance_score(userInput)
            elif action == "get_training_status":
                return self.get_training_status(userInput)
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

        try:
            date = userInput.get('date', None)
            url = f"/wellness-service/wellness/dailySleepData/{self.display_name}"
            params = {"date": str(date), "nonSleepBufferMinutes": 60}
            response = self.call_api(url, params=params)
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in garmin provider: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error in garmin provider")

    def get_user_summary(self, userInput: dict):
        if self.use_test_data:
            response = TEST_DATA["get_user_summary"]
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)

        try:
            date = userInput.get('date', None)
            url = f"/usersummary-service/usersummary/daily/{self.display_name}"
            params = {"calendarDate": str(date)}

            response = self.call_api(url, params=params)

            if response["privacyProtected"] is True:
                raise HTTPException(
                    status_code=500, detail="User data is private")

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in garmin provider: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error in garmin provider")

    def get_body_composition(self, userInput: dict):
        if self.use_test_data:
            response = TEST_DATA["get_body_composition"]
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)

        try:
            date = userInput.get('date', None)
            date_end = userInput.get('date_end', None)
            url = f"/weight-service/weight/dateRange"
            params = {"startDate": str(date), "endDate": str(date_end)}

            response = self.call_api(url, params=params)

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in garmin provider: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error in garmin provider")

    def get_rhr_day(self, userInput: dict):
        if self.use_test_data:
            response = TEST_DATA["get_rhr_day"]
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)

        try:
            date = userInput.get('date', None)
            date_end = userInput.get('date_end', None)
            url = f"/userstats-service/wellness/daily/{self.display_name}"
            params = {
                "fromDate": str(date),
                # if end not set, use start date
                "untilDate": str(date_end or date),
                "metricId": 60,
            }

            response = self.call_api(url, params=params)
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in garmin provider: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error in garmin provider")

    def get_training_readiness(self, userInput: dict):
        if self.use_test_data:
            response = TEST_DATA["get_training_readiness"]
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)

        try:
            date = userInput.get('date', None)
            url = f"/metrics-service/metrics/trainingreadiness/{date}"

            response = self.call_api(url)
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in garmin provider: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error in garmin provider")

    def get_endurance_score(self, userInput: dict):
        if self.use_test_data:
            response = TEST_DATA["get_endurance_score"]
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)

        try:
            date = userInput.get('date', None)
            date_end = userInput.get('date_end', None)
            if date_end is None:
                url = "/metrics-service/metrics/endurancescore"
                params = {"calendarDate": str(date)}
            else:
                url = "/metrics-service/metrics/endurancescore/stats"
                params = {
                    "startDate": str(date),
                    "endDate": str(date_end),
                    "aggregation": "weekly",
                }

            response = self.call_api(url, params=params)
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in garmin provider: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error in garmin provider")

    def get_training_status(self, userInput: dict):
        if self.use_test_data:
            response = TEST_DATA["get_training_status"]
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        try:
            date = userInput.get('date', None)
            url = f"/metrics-service/metrics/trainingstatus/aggregated/{date}"

            response = self.call_api(url)
            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)
        except Exception as e:
            logger.error("Error in garmin provider: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error in garmin provider")
