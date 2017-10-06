#!/usr/bin/env python3

import logging
import math
import os
import random
import threading
import time
import wsclient
from datetime import datetime, timedelta

import LightSchedule
import PCA9685
import PCA9685_dummy
import Pid
import Settings
from WeatherType import WeatherType

Pid = Pid.Pid()
ls = LightSchedule.LightSchedule()
s = Settings.Settings()

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


def catchup_worker(channel, catchup_steps = s.catchup_steps, catchup_time= s.catchup_time):
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
    ws = wsclient
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
        ws.send(msg)
        print(msg)
        if(datetime.now().second == 0):
            logging.info(msg)

        if (cur > goal):
            cur -= 1
        if (cur < goal):
            cur += 1

        if (WEATHER == WeatherType.storm):
            thunderstorm_worker(channel, cur)

        if (WEATHER == WeatherType.cloudy):
            cur = cloud_worker(channel, cur)

        # happy path
        # set
        pwm.set_s(channel, cur)
        time.sleep(sleepTime)

def cloud_worker(channel, c_cur, dim_percent = s.clouds_dim_percent, dim_resolution = s.clouds_dim_resolution, dim_speed = s.clouds_dim_speed):
    '''makes a cloud'''


    init_cur = c_cur
    if channel == random.randint(0, ls.get_number_of_channels()):
        print("{} Cloud Coverage begin channel {} : Cur = {}".format(datetime.now(), channel, c_cur))
        dimTo = round(c_cur * dim_percent)
        dimInterval = round(c_cur / dim_resolution)
        

        while RUN:
            while c_cur > dimTo and WEATHER == WeatherType.cloudy:
                c_cur -= dimInterval
                pwm.set_s(channel, c_cur)
                time.sleep(dim_speed)
            while c_cur < init_cur:
                    c_cur += dimInterval
                    pwm.set_s(channel, c_cur)
                    time.sleep(dim_speed)
            if WEATHER != WeatherType.cloudy:
                return init_cur
            
    return init_cur


def thunderstorm_worker(channel, cur):
    '''makes a thunderstorm'''

    if s.sound_on and channel == 0:
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
        s.load_file()
        # CLOUDY
        if (random.randint(1, 50) == 1 or WEATHER == WeatherType.cloudy):
            try:
                import simpleaudio as sa
                wave_obj = sa.WaveObject.from_wave_file("sound/c1.wav")
                play_obj = wave_obj.play()
            except:
                print("Cant play cloud audio")
            WEATHER = WeatherType.cloudy
            cloudLength = random.randint(30, 60)
            print(timeStr(datetime.now()) + ' : Starting clouds... Length = ' + str(cloudLength))
            logging.info(timeStr(datetime.now()) +
                         ' : Starting clouds... Length = ' + str(cloudLength))
            time.sleep(cloudLength)

        # STORM
        if s.weather=="storm" or (s.storms_random_on and datetime.now().hour >= s.storms_random_start_time and random.randint(1, s.storms_random_freq) == 1):
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
