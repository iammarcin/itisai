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
        "action": "sound_effect",
        "category": "tts",
        "userInput": {"text": "high-quality, professionally recorded footsteps on grass, sound effects foley.", "duration_seconds": 6},
        "userSettings": {"tts": {'voice': "Sherlock"}, "general": {}},
        "customerId": 1
    },
)


print(response.json())
