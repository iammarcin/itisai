import subprocess
from datetime import datetime, timedelta

start_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2024-01-31", "%Y-%m-%d")

current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    subprocess.run(["python", "feed-garmin-data.py",
                   date_str, "get_sleep_data"])
    current_date += timedelta(days=1)
