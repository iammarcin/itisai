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

    # VERY MUCH NEEDED
    def get_user_summary(self, date: str):
        """Return user activity summary for date format 'YYYY-MM-DD'."""

        url = f"/usersummary-service/usersummary/daily/{self.display_name}"
        params = {"calendarDate": str(date)}

        response = self.call_api(url, params=params)

        if response["privacyProtected"] is True:
            raise Exception("User data is private")

        return response

    # VERY MUCH NEEDED
    def get_body_composition(self, start: str, end=None):
        """
        Return available body composition data for 'startdate' format
        'YYYY-MM-DD' through enddate 'YYYY-MM-DD'.
        """
        url = f"/weight-service/weight/dateRange"
        params = {"startDate": str(start), "endDate": str(end)}

        return self.call_api(url, params=params)

    # VERY IMPORTANT - but maybe not - because it could be from garmin.get_training_status
    def get_max_metrics(self, date: str):
        """Return available max metric data for 'date' format 'YYYY-MM-DD'."""

        url = f"/metrics-service/metrics/maxmet/daily/{date}/{date}"
        
        return self.call_api(url)

    # VERY IMPORTANT - but very long
    def get_sleep_data(self, date: str):
        """Return sleep data for current user."""

        url = f"/wellness-service/wellness/dailySleepData/{self.display_name}"
        params = {"date": str(date), "nonSleepBufferMinutes": 60}

        return self.call_api(url, params=params)

    # VERY IMPORTANT 
    def get_rhr_day(self, date: str):
        """Return resting heartrate data for current user."""

        url = f"/userstats-service/wellness/daily/{self.display_name}"
        params = {
            "fromDate": str(date),
            "untilDate": str(date),
            "metricId": 60,
        }

        return self.call_api(url, params=params)


    # important!
    def get_training_readiness(self, date: str):
        """Return training readiness data for current user."""

        url = f"/metrics-service/metrics/trainingreadiness/{date}"

        return self.call_api(url)


    # should be useful - endurance
    def get_endurance_score(self, startdate: str, enddate=None):
        """
        Return endurance score by day for 'startdate' format 'YYYY-MM-DD'
        through enddate 'YYYY-MM-DD'.
        Using a single day returns the precise values for that day.
        Using a range returns the aggregated weekly values for that week.
        """

        if enddate is None:
            url = "/metrics-service/metrics/endurancescore"
            params = {"calendarDate": str(startdate)}

            return self.call_api(url, params=params)
        else:
            url = "/metrics-service/metrics/endurancescore/stats"
            params = {
                "startDate": str(startdate),
                "endDate": str(enddate),
                "aggregation": "weekly",
            }

            return self.call_api(url, params=params)

    # important!
    def get_training_status(self, date: str):
        """Return training status data for current user."""

        url = f"/metrics-service/metrics/trainingstatus/aggregated/{date}"

        return self.call_api(url)

    # probably for weekly report
    def get_activities_by_date(self, startdate, enddate, activitytype=None):
        """
        Fetch available activities between specific dates
        :param startdate: String in the format YYYY-MM-DD
        :param enddate: String in the format YYYY-MM-DD
        :param activitytype: (Optional) Type of activity you are searching
                             Possible values are [cycling, running, swimming,
                             multi_sport, fitness_equipment, hiking, walking, other]
        :return: list of JSON activities
        """

        activities = []
        start = 0
        limit = 20
        # mimicking the behavior of the web interface that fetches
        # 20 activities at a time
        # and automatically loads more on scroll
        url = "/activitylist-service/activities/search/activities"
        params = {
            "startDate": str(startdate),
            "endDate": str(enddate),
            "start": str(start),
            "limit": str(limit),
        }
        if activitytype:
            params["activityType"] = str(activitytype)

        while True:
            params["start"] = str(start)
            act = self.call_api(url, params=params)
            if act:
                activities.extend(act)
                start = start + limit
            else:
                break

        return activities

    # maybe useful - as HR data is not anywhere else 
    def get_activity_hr_in_timezones(self, activity_id):
        """Return activity heartrate in timezones."""

        activity_id = str(activity_id)
        url = f"/activity-service/activity/{activity_id}/hrTimeInZones"

        return self.call_api(url)

    ########################## OTHER METHODS ##########################
    # my tests via watching Network in browser Inspect
    #GET https://connect.garmin.com/fitnessage-service/stats/daily/2024-05-17/2024-06-13?_=1718293562451
    #def get_fitness_age(self, activity_id):
    '''
    [
    {
        "calendarDate": "2024-05-23",
        "values": {
            "bodyFat": 19.299999237060547,
            "achievableFitnessAge": 37.148128020273916,
            "vigorousDaysAvg": 3.0,
            "fitnessAge": 35.37157997937587,
            "rhr": 47
        }
    },
    '''






    ########################## OTHER METHODS ##########################
    # MAYBE IN NEAR FUTURE
    # this is useful if we want gps data (lat/lon to visualize on map)
    def get_activity_details(self, activity_id, maxchart=2000, maxpoly=4000):
        """Return activity details."""

        activity_id = str(activity_id)
        params = {
            "maxChartSize": str(maxchart),
            "maxPolylineSize": str(maxpoly),
        }
        url = f"/activity-service/activity/{activity_id}/details"

        return self.call_api(url, params=params)
      
    # MAYBE LATER
    # maybe useful - if we want more data about trainings
    def get_activity(self, activity_id):
        """Return activity summary, including basic splits."""

        activity_id = str(activity_id)
        url = f"/activity-service/activity/{activity_id}"

        return self.call_api(url)

    # MIGHT BE USEFUL - as a simple summary -number of activities between dates 
    # but i think I'll use get_activities_by_date
    def get_progress_summary_between_dates(
        self, startdate, enddate, metric="distance"
    ):
        """
        Fetch progress summary data between specific dates
        :param startdate: String in the format YYYY-MM-DD
        :param enddate: String in the format YYYY-MM-DD
        :param metric: metric to be calculated in the summary:
            "elevationGain", "duration", "distance", "movingDuration"
        :return: list of JSON activities with their aggregated progress summary
        """

        url = "/fitnessstats-service/activity"
        params = {
            "startDate": str(startdate),
            "endDate": str(enddate),
            "aggregation": "lifetime",
            "groupByParentActivityType": "true",
            "metric": str(metric),
        }

        return self.call_api(url, params=params)

    # probably not useful
    def get_activities_fordate(self, fordate: str):
        """Return available activities for date."""

        url = f"/mobile-gateway/heartRate/forDate/{fordate}"

        return self.call_api(url)    

    # RATHER NOT USEFUL ( avgSleepRespirationValue, which is not in daily summary - but is in sleep)
    def get_respiration_data(self, date: str):
        """Return available respiration data 'date' format 'YYYY-MM-DD'."""

        url = f"/wellness-service/wellness/daily/respiration/{date}"

        return self.call_api(url)
      
    # NOT NEEDED 
    def get_body_battery(self, start: str, end=None):
        """
        Return body battery values by day for 'startdate' format
        'YYYY-MM-DD' through enddate 'YYYY-MM-DD'
        """

        url = f"/wellness-service/wellness/bodyBattery/reports/daily"
        params = {"startDate": str(start), "endDate": str(end)}

        return self.call_api(url, params=params)

    # NOT USEFUL
    def get_activities(self, start, limit):
        """Return available activities."""

        url = "/activitylist-service/activities/search/activities"
        params = {"start": str(start), "limit": str(limit)}

        return self.call_api(url, params=params)

    # no data (i think special training needed)
    def get_hill_score(self, startdate: str, enddate=None):
        """
        Return hill score by day from 'startdate' format 'YYYY-MM-DD'
        to enddate 'YYYY-MM-DD'
        """

        if enddate is None:
            url = "/metrics-service/metrics/hillscore"
            params = {"calendarDate": str(startdate)}

            return self.call_api(url, params=params)

        else:
            url = "/metrics-service/metrics/hillscore/stats"
            params = {
                "startDate": str(startdate),
                "endDate": str(enddate),
                "aggregation": "daily",
            }

            return self.call_api(url, params=params)

    # NOT USEFUL
    # for weights?
    def get_activity_exercise_sets(self, activity_id):
        """Return activity exercise sets."""

        activity_id = str(activity_id)
        url = f"/activity-service/activity/{activity_id}/exerciseSets"

        return self.call_api(url)

    # NOT USEFUL
    def get_workouts(self, start=0, end=10):
        """Return workouts from start till end."""

        url = "/workout-service/workouts"
        params = {"start": start, "limit": end}
        return self.call_api(url, params=params)

    # NOT USEFUL
    def get_workout_by_id(self, workout_id):
        """Return workout by id."""

        url = f"/workout-service/workout/{workout_id}"
        return self.call_api(url)

    # RATHER USELESS
    # NOT NEEDED, we have steps in get_user_summary
    def get_daily_steps(self, start, end):
        """Fetch available steps data 'start' and 'end' format 'YYYY-MM-DD'."""

        url = f"/usersummary-service/stats/steps/daily/{start}/{end}"

        return self.call_api(url)

    # NOT NEEDED
    def get_stress_data(self, date: str):
        """Return stress data for current user."""

        url = f"/wellness-service/wellness/dailyStress/{date}"

        return self.call_api(url)

    # NOT NEEDED 
    def get_heart_rates(self, date):
        """Fetch available heart rates data 'date' format 'YYYY-MM-DD'."""

        url = f"/wellness-service/wellness/dailyHeartRate/{self.display_name}"
        params = {"date": str(date)}

        return self.call_api(url, params=params)


    # looks like duplicated with get_rhr_day
    def get_hrv_data(self, date: str):
        """Return Heart Rate Variability (hrv) data for current user."""

        url = f"/hrv-service/hrv/{date}"

        return self.call_api(url)

    # USELESS
    # we have get_user_summary
    def get_steps_data(self, date):
        """Fetch available steps data for date format 'YYYY-MM-DD'."""

        url = f"/wellness-service/wellness/dailySummaryChart/{self.display_name}"
        params = {"date": str(date)}

        return self.call_api(url, params=params)

    # not sure what it is - no data
    def get_spo2_data(self, date: str):
        """Return available SpO2 data 'date' format 'YYYY-MM-DD'."""

        url = f"/wellness-service/wellness/daily/spo2/{date}"

        return self.call_api(url)