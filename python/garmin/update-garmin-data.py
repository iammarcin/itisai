#!/home/nichu/.venvs/pythonenv/bin/python

from datetime import datetime, timedelta
import sys
import time

from garminHelper import fetch_garmin_data, insert_db_data, get_latest_db_data

########
# this script gets latest data from DB, gets latest date
# and then loops through dates from latest till today
# and fetches data from garmin API and feeds it into my DB
########

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print("Usage: python update-garmin-data.py <action>")
            sys.exit(1)

        # action = "get_sleep_data"
        action = sys.argv[1]

        latest_date_str = get_latest_db_data(action)
        latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")

        # Define the end date as today's date
        end_date = datetime.today()

        # Loop from the next day after the latest date until today
        current_date = latest_date + timedelta(days=1)
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")

            response = fetch_garmin_data(date_str, action)
            print(f"Date: {date_str}, Response: {response}")

            insert_db_data(response, action, date_str)

            print("%s data for day: %s successfully processed" %
                  (action, date_str))

            # for this endpoint - they check how often request is called
            if action == "get_body_composition":
                time.sleep(30)
            else:
                time.sleep(3)

            current_date += timedelta(days=1)
        print("Everything processed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
