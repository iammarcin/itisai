from datetime import datetime, timedelta

from garminHelper import fetch_data, insert_data

start_date = datetime.strptime("2024-07-01", "%Y-%m-%d")
end_date = datetime.strptime("2024-07-01", "%Y-%m-%d")

current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")

    response = fetch_data(date_str, "get_sleep_data")

    insert_data(response, "get_sleep_data", date_str)

    current_date += timedelta(days=1)
