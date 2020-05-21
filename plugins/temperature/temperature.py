import os
import glob
import time
import json
import websockets
import asyncio
from w1thermsensor import W1ThermSensor #https://github.com/timofurrer/w1thermsensor#usage-as-python-package

# ADDED TO BOTTOM OF /boot/config/.txt
# dtoverlay=w1-gpio


### examples
# sensor = W1ThermSensor()
#sensor.set_precision(9)

# temperature_in_celsius = sensor.get_temperature()
# temperature_in_all_units = sensor.get_temperatures([
#     W1ThermSensor.DEGREES_C,
#     W1ThermSensor.DEGREES_F,
#     W1ThermSensor.KELVIN])


#set to lowest resolution precision -- should be faster?
# this needs to be set after every power cycle
#needs root
#for s in W1ThermSensor.get_available_sensors():
#   s.set_precision(9)


def get_temps():
    msg_obj = {}
    msg_obj['temperature'] = []
    
    cnt = 0
    for s in W1ThermSensor.get_available_sensors():
        temp = {}
        temp['id'] = s.id
        temp['name'] = str(cnt)
        temp['value'] = round( s.get_temperature(W1ThermSensor.DEGREES_F), 2)
        temp['unit'] = 'f'
        msg_obj['temperature'].append(temp)
        cnt += 1
    return msg_obj




async def msg_sender():
    async with websockets.connect('ws://localhost:7999/chat/websocket') as websocket:
        while True:
            msg = json.dumps(get_temps())
            print(msg)

            await websocket.send(msg)
            time.sleep(5)

asyncio.get_event_loop().run_until_complete(msg_sender())
