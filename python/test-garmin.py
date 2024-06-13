from garmin.garminProvider import Garmin

garmin = Garmin()
result = garmin.login()
print(result)
''' 
#WORKS WELL
GARTH_HOME = "~/.garmin_session"

try:
  # resume session
  garth.resume(GARTH_HOME)
  garth.client.username
except (FileNotFoundError, GarthException):
    print("Garmin Connect username and password required.")
    
#garth.save(GARTH_HOME)

print(garth.DailySleep.list(period=30))

'''