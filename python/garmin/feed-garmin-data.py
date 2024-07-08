#!/home/nichu/.venvs/pythonenv/bin/python

import sys

from garminHelper import fetch_data, insert_data

########
# this script gets data from Garmin and feeds into DB
# for specific day
########


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Usage: python feed-garmin-data.py <action> <date>")
            sys.exit(1)
        action = sys.argv[1]
        date = sys.argv[2]

        response = fetch_data(date, action)

        insert_data(response, action, date)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
