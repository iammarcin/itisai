import requests
import os
import sys
from datetime import datetime, timedelta


API_URL = "http://localhost:8000/api"
authToken = os.getenv("MY_AUTH_BEARER_TOKEN")

DEBUG = 0

# get data for specific date (from garmin API)
def fetch_data(date, action):

    # for metrics we need to set date_end too (and it has to be specific for Garmin API requirements)
    if action == "get_max_metrics":
        provided_date = datetime.strptime(date, "%Y-%m-%d")

        # if provided_date > today then drop
        if provided_date > datetime.today():
            print("Date is in the future")
            sys.exit(1)
        # unfortunately quite complex calculations for a date
        first_day_last_year_month = (
            provided_date - timedelta(days=365)).replace(day=1) + timedelta(days=31)
        first_day_last_year_month = first_day_last_year_month.replace(day=1)

        # Calculate the last day of the current month
        last_day_current_month = provided_date.replace(
            day=1) + timedelta(days=31)
        last_day_current_month = last_day_current_month.replace(
            day=1) - timedelta(days=1)
        userInput = {
            "date": first_day_last_year_month.strftime("%Y-%m-%d"),
            "date_end": last_day_current_month.strftime("%Y-%m-%d")
        }
    else:
        userInput = {"date": date},

    url = API_URL + "/garmin"
    response = requests.post(
        url,
        headers={"accept": "application/json",
                 "Authorization": "Bearer %s" % authToken},
        json={
            "action": action,
            "category": "provider.garmin",
            "userInput": userInput,
            "userSettings": {
                'general': {'returnTestData': False},
                'provider.garmin': {}
            },
            "customerId": 1
        },
    )
    return response

# having data from garmin API, insert it in DB
def insert_data(response, fetch_data_action, date):
    if DEBUG:
        print("RESPONSE : ", response.json())
    if response.status_code == 200:
        try:
            result = response.json()["message"]["result"]
            data = result if result is not None else {}
            if fetch_data_action == "get_sleep_data":
                action = "insert_sleep_data"
                dataToCheck = data.get(
                    "dailySleepDTO", {}).get("id") is not None
            elif fetch_data_action == "get_user_summary":
                action = "insert_user_summary"
                dataToCheck = data.get('totalKilocalories') is not None
            elif fetch_data_action == "get_body_composition":
                action = "insert_body_composition"
                dataToCheck = data.get('weight') is not None
            elif fetch_data_action == "get_hrv_data":
                action = "insert_hrv_data"
                dataToCheck = data.get('hrvSummary', {}).get(
                    'weeklyAvg') is not None
            elif fetch_data_action == "get_training_readiness":
                action = "insert_training_readiness"
                dataToCheck = data[0].get('score') is not None
                data = data[0]
            elif fetch_data_action == "get_endurance_score":
                action = "insert_endurance_score"
                dataToCheck = data.get('overallScore') is not None
            elif fetch_data_action == "get_fitness_age":
                action = "insert_fitness_age"
                dataToCheck = data.get('chronologicalAge') is not None
            elif fetch_data_action == "get_training_status":
                action = "insert_training_status"
                dataToCheck = data.get('latestTrainingStatusData') is not None
            elif fetch_data_action == "get_max_metrics":
                action = "insert_max_metrics"
                dataToCheck = data[0].get('generic', {}).get(
                    'vo2MaxPreciseValue') is not None
                # we need to transform it to dict (because it's list) - because pydantic expect dict
                data_dict = {entry['generic']
                             ['calendarDate']: entry for entry in data}
                # we need to set the date (that we're checking for) here, because other way it takes calendarDate - and it's monthly
                data_dict['date'] = date
                data = data_dict
            elif fetch_data_action == "get_training_load_balance":
                action = "insert_training_load_balance"
                dataToCheck = data.get(
                    'metricsTrainingLoadBalanceDTOMap') is not None
            else:
                print(f"Unknown action: {fetch_data_action}")
                sys.exit(1)

            db_url = API_URL + "/db"

            if data and dataToCheck:
                db_response = requests.post(
                    db_url,
                    headers={"accept": "application/json",
                             "Authorization": "Bearer %s" % authToken},
                    json={
                        "action": action,
                        "category": "provider.db",
                        "userInput": data,
                        "userSettings": {
                            'general': {'returnTestData': False},
                            'provider.garmin': {}
                        },
                        "customerId": 1
                    }
                )
                print(db_response.json())
            else:
                print(f"No data for {date}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to insert data for {date}: {e}")
    else:
        print(f"Failed to get garmin data for {date}: {response.status_code}")


# get one last entry of data from DB to understand when was the last entry
def get_latest_data(fetch_data_action):
    # for these 2 methods - different useInput - because we don't check when was last entry in DB - but we check existing entries
    # (because get_training_status was executed already and added data - (not) simply we use single table but filling data from 3 different garmin endpoints)
    # so these 2 methods - need to check if data is there - but it's NULL
    if fetch_data_action == "get_max_metrics":
        userInput = {"table": "get_training_status",
                     "ignore_null_vo2max": True,
                     "sort_type": "desc", "offset": 0, "limit": 1}
    elif fetch_data_action == "get_training_load_balance":
        userInput = {"table": "get_training_status",
                     "ignore_null_training_load_data": True,
                     "sort_type": "desc", "offset": 0, "limit": 1}
    else:
        userInput = {"table": fetch_data_action,
                     "sort_type": "desc", "offset": 0, "limit": 1}

    url = API_URL + "/db"
    response = requests.post(
        url,
        headers={"accept": "application/json",
                 "Authorization": "Bearer %s" % authToken},
        json={
            "action": "get_garmin_data",
            "category": "provider.db",
            "userInput": userInput,
            "userSettings": {
                'general': {'returnTestData': False},
                'provider.garmin': {}
            },
            "customerId": 1
        },
    )

    if response.status_code == 200:
        latest_entry = response.json()["message"]["result"][0]
        return latest_entry["calendar_date"]
    else:
        print(f"Failed to get latest data: {response.status_code}")
        sys.exit(1)
