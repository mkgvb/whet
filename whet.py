from __future__ import division

import datetime as dt
import logging
import math
import os
import random
import sys
import threading
import time
from datetime import datetime, timedelta

import pygame  # sounds

import PCA9685
import PCA9685_dummy
import schedule
import Pid
from weatherType import WeatherType

Pid = Pid.Pid()

# LOGGING
logDir = 'logs/'
if not os.path.exists(logDir):
    os.makedirs(logDir)
logging.basicConfig(filename=logDir + str(datetime.now()) + '.log', level=logging.INFO)
# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

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
led_max = 4095  # Max Brightness
led_min = 0     # Min Brightness (off)
run = True
weather = WeatherType.normal
Matrix = schedule.schedule





# Set frequency to 1000hz... LEDS.
pwm.set_pwm_freq(1000)
pwm.set_all(led_min)
time.sleep(1)


def toPercentValue(pwm_val):
  return round(pwm_val/led_max * 100, 2)


def toPwmValue(percent):
  if (percent == 0):
   return led_min
  if (percent == 100):
   return led_max

  percent = percent / 100
  return int(led_max * percent)

def timeStr(t):
  return t.strftime('%H:%M:%S')

cur = led_min
def channel_worker(channel):
  print(timeStr(datetime.now()) + ' : Starting main...')
  cur = led_min
  


  #catchup - runs once
  catchup_steps = 255 
  catchup_time = 5
  x = 1
  print(timeStr(datetime.now()) + ' : Catching up...')
  while cur < toPwmValue(Matrix[datetime.now().hour][channel]):
    cur += toPwmValue(Matrix[datetime.now().hour][channel])/catchup_steps
    cur = int(min(led_max, cur)) #TODO fix this its going over led_max because of rounding
    pwm.set_s(channel,cur)
    x += 1
    time.sleep(catchup_time/catchup_steps)
    

  while run:



    curTime = datetime.now()
    nextHour = curTime + timedelta(hours=1)
    curHour = curTime.hour
    goal = toPwmValue(Matrix[(nextHour.hour)][channel]);
    remainSeconds = 3600 - (curTime.minute * 60 + curTime.second)
    delta = abs(cur - goal)
    sleepTime = int(remainSeconds / delta ) if delta != 0 else 1

    print( timeStr(curTime)
      + "|Channel = " + str(channel)
      + "|Hour = " + str(curHour)
      + "|Goal = "+ str(goal) + "(" + str(toPercentValue(goal)) + "%)"
      + "|Cur = " + str(cur) + "(" + str(toPercentValue(cur)) + "%)"
      + "|Sleep = " + str(sleepTime)
      + "|Delta = " + str(delta)
      + "|Seconds Remain = " + str(remainSeconds))

    logging.info( timeStr(curTime)
      + "|Channel = " + str(channel)
      + "|Hour = " + str(curHour)
      + "|Goal = "+ str(goal) + "(" + str(toPercentValue(goal)) + "%)"
      + "|Cur = " + str(cur) + "(" + str(toPercentValue(cur)) + "%)"
      + "|Sleep = " + str(sleepTime)
      + "|Delta = " + str(delta)
      + "|Seconds Remain = " + str(remainSeconds))

    if (cur > goal ):
      cur -= 1
    if (cur < goal):
      cur += 1



    if (weather == WeatherType.storm):
      thunderstorm_worker( channel, cur)


    #happy path
    #set
    pwm.set_s(channel,cur)
    time.sleep(sleepTime)



def thunderstorm_worker(channel, cur):

  if (channel == 0):
    pygame.mixer.init()
    pygame.mixer.music.load("sounds/chip.mp3")
    pygame.mixer.music.play()
  while (weather == WeatherType.storm and run):

    #dim to percentage of normal weather
    #TODO


    if (random.randint(1,5) == 3):
      pwm.set_s(channel, led_min)
      time.sleep(random.uniform(0, 1))
      pwm.set_s(channel, led_max)
      time.sleep(random.uniform(0, .02))
      print( timeStr(datetime.now())
        + "|Channel = " + str(channel)
        + "|Lightning Strike!")

      if (random.randint(1,5) == 2):
        x = 0
        r = random.randint(-200,200)
        y = random.randint(100,2000)
        while (x < y):
          r = random.randint(-100,200)
          pwm.set_s(channel, x)
          x = x+r
          pwm.set_s(channel, led_min)
          time.sleep(random.uniform(0, .09))

        time.sleep(random.uniform(0, 4))


try:

  threads = []


  for x in range(schedule.channels):
    print(x)                                     # Four times...
    t = threading.Thread(target=channel_worker, args=(x,))
    threads.append(t)
    t.start()                                   # ...Start the thread
    time.sleep(1.1)


  #keep main thread alive
  while True:
    time.sleep(60)

    #CLOUDY
    if (random.randint(1,20) == 5):
      weather= WeatherType.cloudy
      cloudLength = random.randint(30, 60)
      print(timeStr(datetime.now()) + ' : Starting clouds... Length = '+ str(cloudLength))
      logging.info(timeStr(datetime.now()) + ' : Starting clouds... Length = '+ str(cloudLength))
      time.sleep(cloudLength)

    #STORM
    if ((datetime.now().hour > 20) and random.randint(1,1000) == 5 or weather == WeatherType.storm):
      weather = WeatherType.storm
      stormLength = random.randint(60, 120)
      print(timeStr(datetime.now()) + ' : Starting thunderstorm... Length = '+ str(stormLength))
      logging.info(timeStr(datetime.now()) + ' : Starting thunderstorm... Length = '+ str(stormLength))
      time.sleep(stormLength)



    weather = WeatherType.normal

except KeyboardInterrupt:
  logging.info(datetime.now().strftime('%H:%M:%S') +' : KeyboardInterrupt Quit')
  run = False
  pwm.set_all(led_min)


finally:
  logging.info(datetime.now().strftime('%H:%M:%S') +' : finally Quit')
  run = False
  pwm.set_all(led_min)
  Pid.kill()
