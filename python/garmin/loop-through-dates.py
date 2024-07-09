from datetime import datetime, timedelta
import sys
import time

from garminHelper import fetch_garmin_data, insert_db_data

########
# this script loops through manually provided dates
# and fetches data from garmin API and feeds it into my DB
########

if len(sys.argv) < 2:
    print("Usage: python loop-through-dates.py.py <action> <start_date> <end_date>")
    sys.exit(1)

# action = "get_sleep_data"
action = sys.argv[1]

# Set start_date to yesterday and end_date to today if not provided
start_date = datetime.now() - \
    timedelta(days=1) if len(sys.argv) < 3 else datetime.strptime(
        sys.argv[2], "%Y-%m-%d")
end_date = datetime.now() if len(
    sys.argv) < 4 else datetime.strptime(sys.argv[3], "%Y-%m-%d")

current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")

    response = fetch_garmin_data(date_str, action)

    if response.status_code == 200:
        insert_db_data(response, action, date_str)
    else:
        print(
            f"Failed to get data for {date_str}: {response.status_code}")

    # for this endpoint - they check how often request is called
    if action == "get_body_composition":
        time.sleep(30)
    else:
        time.sleep(1)

    current_date += timedelta(days=1)
