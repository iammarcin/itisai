from googleapiclient.discovery import build
import os

api_key = os.environ.get('GOOGLE_MAPS_API_KEY', None)

# GET https://pollen.googleapis.com/v1/forecast:lookup
api_service_name = "pollen"
api_version = "v1"
endpoint = build(api_service_name, api_version, developerKey=api_key)
print(endpoint)
lat = {
    "latitude": 41.7898095,
    "longitude": 3.0238652,
}
metadata = {
    "location": lat,
    "days": 5,
    "plantsDescription": True
}
request = endpoint.forecast().lookup(
    body=metadata
)

response = request.execute()
print(response)

'''
#POST https://airquality.googleapis.com/v1/currentConditions:lookup
api_service_name = "airquality"
api_version = "v1"
endpoint = build(api_service_name, api_version, developerKey=api_key)
print(endpoint)
print(endpoint.currentConditions())
lat = {
    "latitude": 41.7898095,
    "longitude": 3.0238652,
}
metadata = {
    "location": lat
}
request = endpoint.currentConditions().lookup(
    body=metadata
)

response = request.execute()
print(response)



api_service_name = "youtube"
api_version = "v3"
endpoint = build(api_service_name, api_version, developerKey=api_key)
request = endpoint.search().list(
    q="ufc 304",
    part='id,snippet',
    maxResults=10
).execute()


response = request.execute()
print(response)



api_service_name = "pollen"
api_version = "v1"
endpoint = build(api_service_name, api_version, developerKey=api_key)
request = endpoint.forecast().lookup(
    location: {
        "latitude": number,
        "longitude": number
    },
    days: 5,
    plantsDescription: True
)


response = request.execute()
print(response)



api_service_name = "youtube"
api_version = "v3"
youtube = build(api_service_name, api_version, developerKey=api_key)
request = youtube.channels().list(
    part="snippet,contentDetails,statistics",
    id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
)
response = request.execute()
print(response)
'''
