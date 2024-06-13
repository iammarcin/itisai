# WILL BE USED to interact with garmin connect api

"""Thanks to author of https://github.com/cyberjunky/python-garminconnect"""

import logging
import garth

logger = logging.getLogger(__name__)

class Garmin:
  def __init__(self):
    self.garmin_home = "~/.garmin_session"
    self.garth = garth.Client()

    # URLs
    self.user_profile = "/userprofile-service/userprofile/user-settings"

  def connectapi(self, path, **kwargs):
    return self.garth.connectapi(path, **kwargs)

  def login(self):
    try:
      self.garth.load(self.garmin_home)
    except Exception as e:
      print(f"Garmin Connect auth failed. {e}")
      return False

    self.display_name = self.garth.profile["displayName"]
    self.full_name = self.garth.profile["fullName"]

    settings = self.connectapi(self.user_profile)
    self.unit_system = settings["userData"]["measurementSystem"]
    print(f"Logged in as {self.display_name} ({self.full_name})")
    print(f"Unit system: {self.unit_system}")

    return True