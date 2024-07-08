from datetime import datetime, timedelta
import sys

from garminHelper import fetch_data, insert_data

########
# this script loops through manually provided dates
# and fetches data from garmin API and feeds it into my DB
########

if len(sys.argv) < 2:
    print("Usage: python loop-through-dates.py.py <action> <start_date> <end_date>")
    sys.exit(1)

# action = "get_sleep_data"
action = sys.argv[1]

start_date = datetime.strptime("2024-01-02", "%Y-%m-%d") if len(
    sys.argv) < 3 else datetime.strptime(sys.argv[2], "%Y-%m-%d")
end_date = datetime.strptime("2024-01-03", "%Y-%m-%d") if len(
    sys.argv) < 4 else datetime.strptime(sys.argv[3], "%Y-%m-%d")

current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")

    response = fetch_data(date_str, action)

    if response.status_code == 200:
        insert_data(response, action, date_str)
    else:
        print(
            f"Failed to get data for {date_str}: {response.status_code}")

    current_date += timedelta(days=1)
