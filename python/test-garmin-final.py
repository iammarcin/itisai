import requests
import os

authToken = os.getenv("MY_AUTH_BEARER_TOKEN")
# ES
# url = "http://192.168.1.19:8000/chat"
# PT
url = "http://localhost:8000/api/garmin"
response = requests.post(
    url,
    headers={"accept": "application/json",
             "Authorization": "Bearer %s" % authToken},
    json={
        "action": "get_sleep_data",
        "category": "provider.garmin",
        "userInput": {"date": "2024-06-08"},
        "userSettings": {
            'general': {'returnTestData': True},
            'provider.garmin': {}
        },
        "customerId": 1
    },
)

if response.status_code == 200:
    sleep_data = response.json()["message"]["result"]["dailySleepDTO"]
    db_url = "http://localhost:8000/api/db"
    db_response = requests.post(
        db_url,
        headers={"accept": "application/json",
                 "Authorization": "Bearer %s" % authToken},
        json={
            "action": "insert_sleep_data",
            "category": "provider.db",
            "userInput": sleep_data,
            "userSettings": {
                'general': {'returnTestData': False},
                'provider.garmin': {}
            },
            "customerId": 1
        }
    )
    print(db_response.json())
else:
    print(f"Failed to get sleep data: {response.status_code}")
