from garminProvider import Garmin

garmin = Garmin()
result = garmin.login()

response = garmin.get_user_summary("2024-06-06")