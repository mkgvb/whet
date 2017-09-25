#!/usr/bin/env python3
from __future__ import division

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
from WeatherType import WeatherType

Pid = Pid.Pid()
ls = LightSchedule.LightSchedule()


# LOGGING
logDir = 'logs/'
if not os.path.exists(logDir):
    os.makedirs(logDir)
logging.basicConfig(filename=logDir + str(datetime.now()) +
                    '.log', level=logging.INFO)
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


def timeStr(_t):
    return _t.strftime('%H:%M:%S')


cur = LED_MIN


def catchup_worker(channel, catchup_steps=255, catchup_time=5):
    print(timeStr(datetime.now()) + ' : Catching up...')

    curPwm = LED_MIN
    curTime = datetime.now()
    curHour = curTime.hour
    nextHour = (curTime + timedelta(hours=1)).hour
    curGoal = ls.get_pwm(channel, curHour)
    nextGoal = ls.get_pwm(channel, nextHour)
    delta = nextGoal - curGoal
    catchupGoal = curGoal + delta * (curTime.minute / 60)

    # catchup - runs once
    while curPwm < catchupGoal:
        curPwm += round(catchupGoal / catchup_steps)
        pwm.set_s(channel, curPwm)
        #time.sleep(abs(delta) / catchup_steps)
        time.sleep(catchup_time / catchup_steps)
        print(curPwm)

    return curPwm


def channel_worker(channel):
    print(timeStr(datetime.now()) + ' : Starting main...')

    cur = catchup_worker(channel)

    while RUN:

        curTime = datetime.now()
        curHour = curTime.hour
        nextHour = (curTime + timedelta(hours=1)).hour
        goal = ls.get_pwm(channel, nextHour)
        remainSeconds = 3600 - (curTime.minute * 60 + curTime.second)
        delta = abs(cur - goal)
        sleepTime = int(remainSeconds / delta) if delta != 0 else 1

        msg = ""
        msg += timeStr(curTime)
        msg += "|Channel = " + str(channel)
        msg += "|Hour = " + str(curHour)
        msg += "|Goal = " + \
            str(goal) + "(" + str(ls.get_percent(channel, nextHour)) + "%)"
        # Todo the percentage is broken
        msg += "|Cur = " + str(cur) + "(" + str(ls.get_percent_cur(cur)) + "%)"
        msg += "|Sleep = " + str(sleepTime)
        msg += "|Delta = " + str(delta)
        msg += "|Seconds Remain = " + str(remainSeconds)

        #print(msg, end='\r')
        print(msg)
        if(datetime.now().second == 0):
            logging.info(msg)

        if (cur > goal):
            cur -= 1
        if (cur < goal):
            cur += 1

        if (WEATHER == WeatherType.storm):
            thunderstorm_worker(channel, cur)

        # happy path
        # set
        pwm.set_s(channel, cur)
        time.sleep(sleepTime)


def thunderstorm_worker(channel, cur):

    if (channel == 0):
        try:
            import simpleaudio as sa
            wave_obj = sa.WaveObject.from_wave_file("sound/t" + str(random.randint(1, 5)) + ".wav")
            play_obj = wave_obj.play()
        except:
            print("Cant play thunderstorm audio")
    while (WEATHER == WeatherType.storm and RUN):

        # dim to percentage of normal weather
        # TODO

        if (random.randint(1, 5) == 3):
            pwm.set_s(channel, LED_MIN)
            time.sleep(random.uniform(0, 1))
            pwm.set_s(channel, LED_MAX)
            time.sleep(random.uniform(0, .02))
            print(timeStr(datetime.now())
                  + "|Channel = " + str(channel)
                  + "|Lightning Strike!")

            if (random.randint(1, 5) == 2):
                x = 0
                r = random.randint(-200, 200)
                y = random.randint(100, 2000)
                while (x < y):
                    r = random.randint(-100, 200)
                    pwm.set_s(channel, x)
                    x = x + r
                    pwm.set_s(channel, LED_MIN)
                    time.sleep(random.uniform(0, .09))

                time.sleep(random.uniform(0, 4))


try:

    threads = []
    for x in range(ls.get_number_of_channels()):
        t = threading.Thread(target=channel_worker, args=(x,))
        threads.append(t)
        t.start()                                   # ...Start the thread

    # keep main thread alive
    while True:
        time.sleep(60)

        # CLOUDY
        if (random.randint(1, 20) == 5 or WEATHER == WeatherType.cloudy):
            WEATHER = WeatherType.cloudy
            cloudLength = random.randint(30, 60)
            print(timeStr(datetime.now()) +
                  ' : Starting clouds... Length = ' + str(cloudLength))
            logging.info(timeStr(datetime.now()) +
                         ' : Starting clouds... Length = ' + str(cloudLength))
            time.sleep(cloudLength)

        # STORM
        if ((datetime.now().hour > 20) and random.randint(1, 1000) == 5 or WEATHER == WeatherType.storm):
            WEATHER = WeatherType.storm
            stormLength = random.randint(60, 120)
            print(timeStr(datetime.now()) +
                  ' : Starting thunderstorm... Length = ' + str(stormLength))
            logging.info(timeStr(datetime.now()) +
                         ' : Starting thunderstorm... Length = ' + str(stormLength))
            time.sleep(stormLength)

        WEATHER = WeatherType.normal

except KeyboardInterrupt:
    logging.info(datetime.now().strftime(
        '%H:%M:%S') + ' : KeyboardInterrupt Quit')
    RUN = False
    pwm.set_all(LED_MIN)


finally:
    logging.info(datetime.now().strftime('%H:%M:%S') + ' : finally Quit')
    RUN = False
    pwm.set_all(LED_MIN)
    Pid.kill()
