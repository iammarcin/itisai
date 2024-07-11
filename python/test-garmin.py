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
        "action": "get_activity",
        "category": "provider.garmin",
        "userInput": {"date": "2024-07-05", "activity_id": "15367619474"},
        # "userInput": {"date": "2024-01-07", "date_end": "2024-07-08"},
        # "userInput": {"date": "2024-07-07", "end_date": "2024-06-19"},
        # "userInput": {"sort_type": "desc", "offset": 0, "limit": 1},
        "userSettings": {'text': {
            'temperature': 0.05, 'model': 'GPT-3.5', 'memory_limit': 680,
            'ai_character': 'assistant', 'streaming': True},
            'tts': {'stability': 0, 'similarity_boost': 0, 'voice': 'alloy', 'streaming':
                    True, 'speed': 1, 'model': 'tts-1'}, 'speech': {'language': 'en', 'temperature': 0},
            'image': {'model': 'dall-e-3', 'number_of_images': 1, 'size_of_image': 1024, 'quality_hd': False, 'disable_safe_prompt_adjust': False},
            'general': {'returnTestData': False},
            'provider.garmin': {}
        },
        "customerId": 1
    },
)

for chunk in response.iter_content(chunk_size=12):
    if chunk:
        print(str(chunk, encoding="utf-8"), end="")


'''
# get_sleep_data
sleepTimeSeconds
napTimeSeconds



'''

''' 
from garmin.garminProvider import Garmin

garmin = Garmin()
result = garmin.login()
print(result)

#WORKS WELL
GARTH_HOME = "~/.garmin_session"

try:
  # resume session
  garth.resume(GARTH_HOME)
  garth.client.username
except (FileNotFoundError, GarthException):
    print("Garmin Connect username and password required.")
    
#garth.save(GARTH_HOME)

print(garth.DailySleep.list(period=30))

'''
