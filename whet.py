#!/usr/bin/env python3
import logging
import Server
import time
import os
# Logs----------------------------------------------------------
DEBUG = False
LOGDIR = 'logs/'
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')

handler = logging.handlers.TimedRotatingFileHandler(LOGDIR + "whet.log",
                                                    when='midnight',
                                                    interval=1,
                                                    backupCount=7)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

debug_handler = logging.handlers.TimedRotatingFileHandler(LOGDIR + "whet-DEBUG.log",
                                                          when='midnight',
                                                          interval=1,
                                                          backupCount=2)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)
logger.addHandler(debug_handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

logging.info("Whet started")

# Server----------------------------------------------------------
Server = Server.Server()
Server.start()
time.sleep(1)

import math
import random
import threading
import wsclient
from datetime import datetime, timedelta

import LightSchedule
import PCA9685
import PCA9685_dummy
import Pid
import Settings
import Channel
from WeatherType import WeatherType

#Pid = Pid.Pid()
ls = LightSchedule.LightSchedule()
s = Settings.Settings()
ws = wsclient

# Uncomment to enable debug output.
#import logging
# logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685, if cant use a dummy (for testing on machine that is not pi)
try:
    pwm = PCA9685.PCA9685()
    # Alternatively specify a different address and/or bus:
    #pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
except:
    msg = "UNABLE TO LOAD PCA9685... no pwm values will set!"
    logging.warn(msg)
    print(msg)
    pwm = PCA9685_dummy.PCA9685()


# Configure min and max, initial weather pattern
LED_MAX = 4095  # Max Brightness
LED_MIN = 0     # Min Brightness (off)
WEATHER = WeatherType.normal


# Set frequency to 1000hz... LEDS.
pwm.set_pwm_freq(1000)
pwm.set_all(LED_MIN)
time.sleep(1)

try:
    channel_threads = []
    for i in range(ls.get_number_of_channels()):
        channelObj = Channel.Channel(i, pwm, ls)
        channel_threads.append(channelObj)
        channelObj.start()

    # keep main thread alive
    while True:
        s.load_file()
        time.sleep(15)
        s.dump_file()

except KeyboardInterrupt:
    logging.info(datetime.now().strftime(
        '%H:%M:%S') + ' : KeyboardInterrupt Quit')

    pwm.set_all(LED_MIN)
finally:
    logging.info(datetime.now().strftime('%H:%M:%S') + ' : finally Quit')
    for i in range(len(channel_threads)):
        channel_threads[i].cancel()
    pwm.set_all(LED_MIN)
    # Pid.kill()
    Server.stop()


if __name__ == "main":
    pass
