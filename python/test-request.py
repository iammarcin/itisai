import requests
import os
authToken = os.getenv("MY_AUTH_BEARER_TOKEN")
# ES
# url = "http://192.168.1.19:8000/generate"
# PT
url = "http://localhost:8000/generate"
response = requests.post(
    url,
    headers={"accept": "application/json",
             "Authorization": "Bearer %s" % authToken},
    json={
        "action": "billing",
        "category": "tts",
        "userInput": {"text": "test"},
        "userSettings": {"tts": {'voice': "Sherlock"}, "general": {}},
        "customerId": 1
    },
)


print(response.json())
