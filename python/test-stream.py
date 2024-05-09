#https://tech.clevertap.com/streaming-openai-app-in-python/

import requests
# HOME
#url = "http://192.168.1.19:8000/chatstream"
# PT
url = "http://192.168.23.66:8000/chatstream"
response = requests.post(
    url,
    headers={"accept": "application/json"},
    json=
        {
            "action": "text",
            "userInput": { "prompt": "List 10 interesting things to do"},
            "userSettings": { "generator": "openai", },
            "customerId": 1
        },
    stream=True
)

for chunk in response.iter_content(chunk_size=12):
    if chunk:
        print(str(chunk, encoding="utf-8"), end="")
