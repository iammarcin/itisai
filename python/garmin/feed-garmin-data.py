import requests
import os
import sys

API_URL = "http://localhost:8000/api"
authToken = os.getenv("MY_AUTH_BEARER_TOKEN")


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


def insert_data(response, insert_data_action):
    if response.status_code == 200:
        data = None
        if insert_data_action == "get_sleep_data":
            action = "insert_sleep_data"
            data = response.json()["message"]["result"]["dailySleepDTO"]

        db_url = API_URL + "/db"

        if data:
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


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Usage: python feed-garmin-data.py <date> <action>")
            sys.exit(1)
        date = sys.argv[1]
        action = sys.argv[2]
        response = fetch_data(date, action)

        insert_data(response, action)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
