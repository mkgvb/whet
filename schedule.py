import json
import LightSchedule
import time

CHANNELS = 2
HOURS = 24
schedule = [[0 for x in range(CHANNELS)] for y in range(HOURS)]


# these default to 0 if not set
for x in range(CHANNELS):
    schedule[8][x] = 0  # 8AM
    schedule[9][x] = 0
    schedule[10][x] = 0
    schedule[11][x] = 0
    schedule[12][x] = 0
    schedule[13][x] = 10  # 01PM
    schedule[14][x] = 30
    schedule[15][x] = 30
    schedule[16][x] = 200
    schedule[17][x] = 100  # 05PM
    schedule[18][x] = 100
    schedule[19][x] = 100
    schedule[20][x] = 80
    schedule[21][x] = 50  # 9PM
    schedule[22][x] = 0
    schedule[23][x] = 0

while True:
    lights = LightSchedule.LightSchedule()
    print (lights.GetPwm(0,13))
    print (lights.GetPwm(0,14))
    print (lights.GetPwm(0,15))
    print (lights.GetPwm(0,16))
    print (lights.GetPercent(0,25))
    time.sleep(2)
