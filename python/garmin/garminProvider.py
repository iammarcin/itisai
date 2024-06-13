# WILL BE USED to interact with garmin connect api

"""Thanks to author of https://github.com/cyberjunky/python-garminconnect"""

import garth
import logconfig

logger = logconfig.logger

class Garmin:
    def __init__(self):
        self.garmin_home = "~/.garmin_session"
        self.garth = garth.Client()
        self.display_name = None
        self.full_name = None
        self.unit_system = None

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

        settings = self.call_api("/userprofile-service/userprofile/user-settings")
        
        self.unit_system = settings["userData"]["measurementSystem"]
        logger.debug(f"Logged in as {self.display_name} ({self.full_name})")
        logger.debug(f"Unit system: {self.unit_system}")

        return True

    def get_user_summary(self, date: str):
        """Return user activity summary for 'curr date' format 'YYYY-MM-DD'."""

        url = f"/usersummary-service/usersummary/daily/{self.display_name}"
        params = {"calendarDate": str(date)}

        response = self.call_api(url, params=params)

        if response["privacyProtected"] is True:
            raise Exception("User data is private")

        return response