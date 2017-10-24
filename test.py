#!/usr/bin/env python3

import logging
import math
import os
import random
import threading
import time
from datetime import datetime, timedelta

import LightSchedule
import PCA9685
import PCA9685_dummy
import Pid
import Settings
from WeatherType import WeatherType


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
    i = 0
    j = 0
    while RUN:
        
        while j < LED_MAX:
            pwm.set_all(j)
            j += 1
        while j > LED_MIN:
            pwm.set_all(j)
            j -= 1
        time.sleep(1)

        for c in range(0,5):
            while i < LED_MAX:
                pwm.set_s(c, min(LED_MAX,i))
                i += 1
                #time.sleep(.5)
                print(i)
            time.sleep(1)
            while i > LED_MIN:
                pwm.set_s(c, i)
                i -= 1
                print(i)
            print("bottom" + str(i))
            time.sleep(1)
finally:
    logging.info(datetime.now().strftime('%H:%M:%S') + ' : finally Quit')
    RUN = False
    pwm.set_all(LED_MIN)
