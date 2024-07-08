from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import json
import os
import logging
from datetime import datetime, date

import logconfig
import config as config

logger = logconfig.logger

DEBUG = config.defaults["DEBUG"]
VERBOSE_SUPERB = config.defaults["VERBOSE_SUPERB"]

class WithingsConfig:
    """This class takes care of the Withings config file"""

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.read()

    def read(self):
        """reads config file"""
        try:
            with open(self.config_file, encoding="utf8") as configfile:
                return json.load(configfile)
        except (ValueError, FileNotFoundError):
            logger.error("Can't read config file %s", self.config_file)
            return {}

class WithingsOAuth2:
    """This class takes care of the Withings OAuth2 authentication"""

    AUTHORIZE_URL = "https://account.withings.com/oauth2_user/authorize2"
    TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"
    GETMEAS_URL = "https://wbsapi.withings.net/measure?action=getmeas"

    def __init__(self, app_config_file, user_config_file):
        self.app_config = WithingsConfig(app_config_file).config
        self.user_cfg = WithingsConfig(user_config_file)
        self.user_config = self.user_cfg.config

        if not self.user_config.get("access_token"):
            if not self.user_config.get("authentification_code"):
                self.user_config["authentification_code"] = self.get_authentication_code(
                )
            try:
                self.get_access_token()
            except Exception:
                logger.warning(
                    "Could not get access-token. Trying to renew auth_code")
                self.user_config["authentification_code"] = self.get_authentication_code(
                )
                self.get_access_token()

    def get_authentication_code(self):
        """get Withings authentication code"""
        params = {
            "response_type": "code",
            "client_id": self.app_config["client_id"],
            "state": "OK",
            "scope": "user.metrics",
            "redirect_uri": self.app_config["callback_url"],
        }

        logger.warning(
            "User interaction needed to get Authentication Code from Withings!")
        url = self.AUTHORIZE_URL + "?" + \
            "&".join(f"{k}={v}" for k, v in params.items())
        logger.info(url)
        authentification_code = input("Token: ")
        return authentification_code

    def get_access_token(self):
        """get Withings access token"""
        logger.info("Get Access Token")

        params = {
            "action": "requesttoken",
            "grant_type": "authorization_code",
            "client_id": self.app_config["client_id"],
            "client_secret": self.app_config["consumer_secret"],
            "code": self.user_config["authentification_code"],
            "redirect_uri": self.app_config["callback_url"],
        }

        req = requests.post(self.TOKEN_URL, data=params)
        resp = req.json()

        if resp.get("status") != 0:
            logger.error("Error: %s", resp)
            raise HTTPException(
                status_code=500, detail="Failed to get access token")

        body = resp.get("body")
        self.user_config.update({
            "access_token": body.get("access_token"),
            "refresh_token": body.get("refresh_token"),
            "userid": body.get("userid"),
        })
        # self.user_cfg.write()

    def refresh_access_token(self):
        """refresh Withings access token"""
        logger.info("Refresh Access Token")

        params = {
            "action": "requesttoken",
            "grant_type": "refresh_token",
            "client_id": self.app_config["client_id"],
            "client_secret": self.app_config["consumer_secret"],
            "refresh_token": self.user_config["refresh_token"],
        }

        req = requests.post(self.TOKEN_URL, data=params)
        resp = req.json()

        if resp.get("status") != 0:
            logger.error("Error: %s", resp)
            raise HTTPException(
                status_code=500, detail="Failed to refresh access token")

        body = resp.get("body")
        self.user_config.update({
            "access_token": body.get("access_token"),
            "refresh_token": body.get("refresh_token"),
            "userid": body.get("userid"),
        })
        # self.user_cfg.write()

class WithingsProvider:
    def __init__(self, app_config_file, user_config_file):
        self.withings = WithingsOAuth2(app_config_file, user_config_file)

    def get_body_composition(self, target_date, height=188):
        """get Withings body composition data"""
        logger.info("Get Body Composition")

        # Convert date string to datetime object. and let's check from beginning till end of the date
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
        startdate = datetime(
            target_date.year, target_date.month, target_date.day, 0, 0, 0)
        enddate = datetime(target_date.year, target_date.month,
                           target_date.day, 23, 59, 59)

        try:
            self.withings.refresh_access_token()
        except HTTPException:
            logger.warning(
                "Failed to refresh access token, trying to get a new one")
            self.withings.get_access_token()

        params = {
            "access_token": self.withings.user_config["access_token"],
            "category": 1,
            "startdate": int(startdate.timestamp()),
            "enddate": int(enddate.timestamp()),
        }

        req = requests.post(WithingsOAuth2.GETMEAS_URL, params=params)
        measurements = req.json()
        logger.info("req: %s", req)
        logger.info("measurements: %s", measurements)
        if measurements.get("status") != 0:
            logger.error("Error fetching measurements: %s", measurements)
            raise HTTPException(
                status_code=500, detail="Failed to get body composition")

        body_measures = []
        try:

            for group in measurements.get("body", {}).get("measuregrps", []):
                measures = {m["type"]: m["value"] *
                            (10 ** m["unit"]) for m in group["measures"]}
                print(group)
                print(measures)

                measure_group = {
                    "calendar_date": datetime.fromtimestamp(group["date"]).strftime('%Y-%m-%d'),
                    "weight": measures.get(1),
                    "bmi": 0,
                    "body_fat_mass": measures.get(8),
                    "body_fat_percentage": measures.get(6),
                    "body_water_mass": measures.get(77),
                    "body_water_percentage": 0,
                    "bone_mass": measures.get(88),
                    "bone_mass_percentage": 0,
                    "muscle_mass": measures.get(76),
                    "muscle_mass_percentage": 0,
                    "visceral_fat": measures.get(170),
                    "vascular_age": measures.get(155)
                }

                # Filter out entries with all null values
                if any(value is not None for key, value in measure_group.items() if key != "calendar_date"):
                    body_measures.append(measure_group)
        except Exception as e:
            logger.error("Error fetching measurements: %s", e)
            raise HTTPException(
                status_code=500, detail="Failed to get body composition")
        return body_measures
