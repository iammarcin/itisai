#!/home/nichu/.venvs/pythonenv/bin/python

from datetime import datetime, timedelta
from requests.models import Response
import sys
import time

from garminHelper import fetch_garmin_data, insert_db_data, get_latest_db_data

# wait between API calls
TIME_SLEEP = 5

# in insert_db_data we need to provide requests.models.Response type of data, not dict
# so we need to create this custom class to pass proper data
class CustomResponse(Response):
    def __init__(self, activity, status_code=200):
        super().__init__()
        self._activity = activity
        self.status_code = status_code

    def json(self):
        return {
            "message": {
                "result": self._activity
            }
        }

def loop_through_trainings(data, date):
    try:
        for activity in data:
            # Fetch heart rate zone data for the activity
            activity_id = activity["activityId"]
            response = fetch_garmin_data(
                date, "get_activity_hr_in_timezones", additionalParams={"activity_id": activity_id})

            if response.status_code == 200:
                zones_data = response.json().get("message", {}).get("result", [])
                activity["zones"] = zones_data

            response_data = CustomResponse(
                activity, status_code=response.status_code)

            insert_db_data(response_data, "get_activities", date)

            # and now GPS data
            response = fetch_garmin_data(
                date, "get_activity", additionalParams={"activity_id": activity_id})

            # there will be activities with no GPS data (like pilates), so we don't want to save them to DB
            saveToDB = False

            if response.status_code == 200:
                gps_data = response.json().get("message", {}).get("result", [])
                gps_data["activity_date"] = activity.get(
                    "startTimeLocal").split(" ")[0]
                gps_data["activity_name"] = activity["activityName"]
                # Check if both directLongitude and directLatitude are present
                if gps_data.get("metricDescriptors"):
                    metrics_indices = {desc["key"]: desc["metricsIndex"]
                                       for desc in gps_data.get("metricDescriptors", [])}
                    if "directLongitude" in metrics_indices or "directLatitude" in metrics_indices:
                        saveToDB = True

            if saveToDB:
                print("Processing GPS data")
                response_gps_data = CustomResponse(
                    gps_data, status_code=response.status_code)
                insert_db_data(response_gps_data,
                               "get_activity_gps_data", date)
            else:
                print("Skipping GPS data")

            print("Activity_id: %s processed! \n" % activity_id)

            time.sleep(TIME_SLEEP)

    except Exception as e:
        print(f"Error while processing activities: {e}")


if __name__ == "__main__":
    try:
        loop_through_dates = False

        date = sys.argv[1] if len(sys.argv) > 1 else None
        date_end = sys.argv[2] if len(sys.argv) > 2 else None

        # if date not provided - it means that we want to check when was latest and loop through dates till today
        # and if provided - we just want single day
        if date is None:
            # get latest date from DB
            latest_date_str = get_latest_db_data("get_activities")
            latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
            activities_end_date = datetime.today()
            loop_through_dates = True

        if date_end is not None:
            latest_date = datetime.strptime(date, "%Y-%m-%d")
            activities_end_date = datetime.strptime(date_end, "%Y-%m-%d")
            loop_through_dates = True

        if loop_through_dates:
            # Define the end date as today's date

            # we start from latest day, not latest + 1 - because there might be more trainings uploaded same day (and if something we will just overwrite it)
            current_date = latest_date

            while current_date <= activities_end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                response = fetch_garmin_data(date_str, "get_activities")
                activities_data = response.json()["message"]["result"]
                loop_through_trainings(activities_data, date_str)
                time.sleep(TIME_SLEEP)
                current_date += timedelta(days=1)
                print("Activities for day: %s successfully processed" % date_str)
        else:
            # get data for specific date from garmin provider
            response = fetch_garmin_data(
                date, "get_activities")

            if response.status_code == 200:
                if response.json()["message"]["result"] == []:
                    print("No trainings for this date")
                    sys.exit(0)
                else:
                    activities_data = response.json()["message"]["result"]
                    loop_through_trainings(activities_data, date)
                    print(
                        "Activities for day: %s successfully processed \n\n" % date)
            else:
                print(
                    f"Failed to get data for {date}: {response.status_code}")
                sys.exit(1)

        print("Everything processed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
