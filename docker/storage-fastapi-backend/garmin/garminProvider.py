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
        self.set_settings(userSettings)
        date = userInput.get('date', None)
        date_end = userInput.get('date_end', None)

        if not date:
            raise HTTPException(
                status_code=400, detail="Date is required for Garmin provider")

        actions_map = {
            "get_sleep_data": "/wellness-service/wellness/dailySleepData/{self.display_name}",
            "get_user_summary": "/usersummary-service/usersummary/daily/%s " % self.display_name,
            "get_body_composition": "/weight-service/weight/dateRange",
            "get_hrv_data": "/hrv-service/hrv/%s" % date,
            "get_training_readiness": "/metrics-service/metrics/trainingreadiness/%s" % date,
            "get_endurance_score": "/metrics-service/metrics/endurancescore/stats" if date_end is not None else "/metrics-service/metrics/endurancescore",
            "get_training_status": "/metrics-service/metrics/trainingstatus/daily/%s" % date,
            "get_training_load_balance": "metrics-service/metrics/trainingloadbalance/latest/%s" % date,
            "get_max_metrics": "metrics-service/metrics/maxmet/latest/%s" % date,
            "get_fitness_age": "fitnessage-service/fitnessage/%s" % date,
        }

        if action not in actions_map:
            raise HTTPException(status_code=400, detail="Unknown action")

        try:
            if self.use_test_data:
                response = TEST_DATA[action]
            else:
                url = actions_map[action]

                print("URL: ", url)
                params = self.construct_params(action, userInput)
                response = self.call_api(url, params=params)

                if action == "get_user_summary" and response.get("privacyProtected"):
                    raise HTTPException(
                        status_code=500, detail="User data is private")

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": response}}, status_code=200)

        except Exception as e:
            logger.error("Error processing Garmin request: %s", str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Error processing Garmin request")

    def construct_params(self, action, userInput):
        date = userInput.get('date', None)
        date_end = userInput.get('date_end', None)

        if action == "get_sleep_data":
            return {"date": str(date), "nonSleepBufferMinutes": 60}
        elif action == "get_user_summary":
            return {"calendarDate": str(date)}
        elif action == "get_body_composition":
            return {"startDate": str(date), "endDate": str(date_end or date)}
        elif action in ["get_hrv_data", "get_max_metrics", "get_training_load_balance", "get_fitness_age", "get_training_readiness", "get_training_status"]:
            return None
        elif action == "get_endurance_score":
            if date_end is None:
                return {"calendarDate": str(date)}
            else:
                return {"startDate": str(date), "endDate": str(date_end), "aggregation": "weekly"}

        return {}
