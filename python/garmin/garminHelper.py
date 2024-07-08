import requests
import os
import sys

API_URL = "http://localhost:8000/api"
authToken = os.getenv("MY_AUTH_BEARER_TOKEN")

DEBUG = 0

# get data for specific date (from garmin API)
def fetch_data(date, action):
    url = API_URL + "/garmin"
    response = requests.post(
        url,
        headers={"accept": "application/json",
                 "Authorization": "Bearer %s" % authToken},
        json={
            "action": action,
            "category": "provider.garmin",
            "userInput": {"date": date},
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
        result = response.json()["message"]["result"]
        data = result if result is not None else {}
        if fetch_data_action == "get_sleep_data":
            action = "insert_sleep_data"
            dataToCheck = data.get("dailySleepDTO", {}).get("id") is not None
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
            dataToCheck = data.get('generic', {}).get(
                'vo2MaxPreciseValue') is not None
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
    else:
        print(f"Failed to get garmin data for {date}: {response.status_code}")


# get one last entry of data from DB to understand when was the last entry
def get_latest_data(fetch_data_action):

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
