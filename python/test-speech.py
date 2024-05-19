import requests
## ES
#url = "http://192.168.1.19:8000/generate"
## PT
url = "http://192.168.23.66:8000/generate"
response = requests.post(
    url,
    headers={"accept": "application/json"},
    json=
        {
            "action": "transcribe",
            "category": "speech",
            "userInput": { },
            "userSettings": { "speech": {}, "general": {} },
            "customerId": 1
        },
)


print(response.json())