#!/usr/bin/env python3
import logging
import Server
import time
from logging.handlers import TimedRotatingFileHandler
import os
#Logs----------------------------------------------------------
logDir = 'logs/'
if not os.path.exists(logDir):
    os.makedirs(logDir)
handler = TimedRotatingFileHandler(logDir+"whet.log",
                                    when='midnight',
                                    interval=1,
                                    backupCount=7)
logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    handlers=[handler])

logging.info("Whet started")

#Server----------------------------------------------------------
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

Pid = Pid.Pid()
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
    msg = "WARNING - unable to load PWM chip... no values will set!"
    logging.info(msg)
    print(msg)
    pwm = PCA9685_dummy.PCA9685()


# Configure min and max, initial weather pattern
LED_MAX = 4095  # Max Brightness
LED_MIN = 0     # Min Brightness (off)
RUN = True
WEATHER = WeatherType.normal


# Set frequency to 1000hz... LEDS.
pwm.set_pwm_freq(1000)
pwm.set_all(LED_MIN)
time.sleep(1)

try:
    threads = []
    for i in range(ls.get_number_of_channels()):
        channelObj = Channel.Channel(i, pwm)
        threads.append(channelObj)
        channelObj.start()

    # keep main thread alive
    while True:
        
        time.sleep(15)
        s.load_file()
        s.broadcast()
        ls.broadcast()

        # RANDOM CLOUDY
        if (WEATHER == WeatherType.cloudy):
            try:
                import simpleaudio as sa
                wave_obj = sa.WaveObject.from_wave_file("sound/c1.wav")
                play_obj = wave_obj.play()
            except:
                logging.warn("Cant play cloud audio")
            WEATHER = WeatherType.cloudy
            cloudLength = random.randint(30, 60)
            logging.info('Starting clouds... Length = ' + str(cloudLength))
            time.sleep(cloudLength)

        # RANDOM STORM
        if s.weather=="storm" or (s.storms_random_on and datetime.now().hour >= s.storms_random_start_time and random.randint(1, s.storms_random_freq) == 1):
            WEATHER = WeatherType.storm
            stormLength = random.randint(60, 120)
            logging.info('Starting thunderstorm... Length = ' + str(stormLength))
            time.sleep(stormLength)

        s.weather = "normal"
        s.dump_file()

except KeyboardInterrupt:
    logging.info(datetime.now().strftime(
        '%H:%M:%S') + ' : KeyboardInterrupt Quit')

    pwm.set_all(LED_MIN)


finally:
    logging.info(datetime.now().strftime('%H:%M:%S') + ' : finally Quit')
    for i in range(len(threads)):
        threads[i].cancel()
    pwm.set_all(LED_MIN)
    Pid.kill()
    Server.stop()
