import requests
import os
import sys

from garminHelper import fetch_data, insert_data

if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Usage: python feed-garmin-data.py <date> <action>")
            sys.exit(1)
        date = sys.argv[1]
        action = sys.argv[2]
        response = fetch_data(date, action)

        insert_data(response, action, date)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
