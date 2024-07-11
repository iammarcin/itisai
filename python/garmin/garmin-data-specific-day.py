#!/home/nichu/.venvs/pythonenv/bin/python

import sys

from garminHelper import fetch_garmin_data, insert_db_data

########
# this script gets data from Garmin and feeds into DB
# for specific day
########


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Usage: python garmin-data-specific-day.py <action> <date>")
            sys.exit(1)
        action = sys.argv[1]
        date = sys.argv[2]

        response = fetch_garmin_data(date, action)
        insert_db_data(response, action, date)

        print("%s data for day: %s successfully processed" % (action, date))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
