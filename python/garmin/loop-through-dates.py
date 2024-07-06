from datetime import datetime, timedelta

from garminHelper import fetch_data, insert_data

########
# this script loops through manually provided dates
# and fetches data from garmin API and feeds it into my DB
########

action = "get_sleep_data"

start_date = datetime.strptime("2024-07-06", "%Y-%m-%d")
end_date = datetime.strptime("2024-07-06", "%Y-%m-%d")

current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")

    response = fetch_data(date_str, action)

    if response.status_code == 200:
        response_json = response.json()
        if response_json["message"]["result"]["dailySleepDTO"]["id"] is not None:
            insert_data(response, action, date_str)
        else:
            print(f"No sleep data for {date_str}")
    else:
        print(
            f"Failed to get sleep data for {date_str}: {response.status_code}")

    current_date += timedelta(days=1)
