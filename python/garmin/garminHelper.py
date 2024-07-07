import requests
import os
import sys

API_URL = "http://localhost:8000/api"
authToken = os.getenv("MY_AUTH_BEARER_TOKEN")

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
    if response.status_code == 200:
        data = None
        if fetch_data_action == "get_sleep_data":
            action = "insert_sleep_data"
            data = response.json()["message"]["result"]
        else:
            print(f"Unknown action: {fetch_data_action}")
            sys.exit(1)

        db_url = API_URL + "/db"

        if data and data["dailySleepDTO"]["id"] is not None:
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
        print(f"Failed to get sleep data for {date}: {response.status_code}")


# get one last entry of data from DB to understand when was the last entry
def get_latest_data(fetch_data_action):

    if fetch_data_action == "get_sleep_data":
        userInput = {"table": fetch_data_action,
                     "sort_type": "desc", "offset": 0, "limit": 1}
    else:
        print(f"Unknown action: {fetch_data_action}")
        sys.exit(1)

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
