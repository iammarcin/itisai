import requests
import os
authToken = os.getenv("MY_AUTH_BEARER_TOKEN")

# ES
# url = "http://192.168.1.19:8000/chatstream"
# PT

# model claude-3-5-sonnet
url = "http://localhost:8000/chat"
response = requests.post(
    url,
    headers={"accept": "application/json",
             "Authorization": "Bearer %s" % authToken},
    json={
        "action": "chat",
        "category": "text",
        "userInput": {"prompt": "List 1 interesting thing to do"},
        "userSettings": {
            'text': {
                'temperature': 0.05, 'model': 'claude-3-5-sonnet', 'memory_limit': 680,
                'ai_character': 'assistant', 'streaming': True},
            'tts': {'stability': 0, 'similarity_boost': 0, 'voice': 'alloy', 'streaming':
                    True, 'speed': 1, 'model': 'tts-1'}, 'speech': {'language': 'en', 'temperature': 0},
            'image': {'model': 'dall-e-3', 'number_of_images': 1, 'size_of_image': 1024, 'quality_hd': False, 'disable_safe_prompt_adjust': False},
            'general': {'returnTestData': False},
            'provider.garmin': {}
        }, "customerId": 1
    },
    stream=True
)

for chunk in response.iter_content(chunk_size=12):
    if chunk:
        print(str(chunk, encoding="utf-8"), end="")
