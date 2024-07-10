#!/home/nichu/.venvs/pythonenv/bin/python

from datetime import datetime, timedelta
from requests.models import Response
import sys
import time

from garminHelper import fetch_garmin_data, insert_db_data, get_latest_db_data


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
            print("Activity processed. Date: %s , activity_id: %s" %
                  (date, activity_id))

    except Exception as e:
        print(f"Error while processing activities: {e}")


if __name__ == "__main__":
    try:
        date = None
        # if date not provided - it means that we want to check when was latest and loop through dates till today
        # and if provided - we just want single day
        loop_through_dates = False
        if len(sys.argv) == 2:
            date = sys.argv[1]

        if date is None:
            # get latest date from DB
            latest_date_str = get_latest_db_data("get_activities")
            latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
            loop_through_dates = True

        if loop_through_dates:
            # Define the end date as today's date
            end_date = datetime.today()
            # we start from latest day, not latest + 1 - because there might be more trainings uploaded same day (and if something we will just overwrite it)
            current_date = latest_date

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                response = fetch_garmin_data(date_str, "get_activities")
                activities_data = response.json()["message"]["result"]
                loop_through_trainings(activities_data, date_str)
                time.sleep(1)
                current_date += timedelta(days=1)
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
            else:
                print(
                    f"Failed to get data for {date}: {response.status_code}")
                sys.exit(1)

        if loop_through_dates:
            # Define the end date as today's date
            end_date = datetime.today()
            # end_date = "2024-01-07"
            # we start from latest day - because there might be more trainings uploaded same day (and if something we will just overwrite it)
            current_date = latest_date

            print("latest_date: ", latest_date)

        print("Everything processed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
