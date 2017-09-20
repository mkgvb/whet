from __future__ import division
import time
from datetime import datetime
from datetime import timedelta
import datetime as dt
import random
import math
import logging
import threading
import os
from weatherType import WeatherType
import PCA9685
import PCA9685_dummy
import sys
import pygame


pid = str(os.getpid())
pidfile = "/tmp/whet.pid"

#PID CHECK
if os.path.isfile(pidfile):
    print "%s already exists, exiting" % pidfile
    sys.exit()
file(pidfile, 'w').write(pid)

# LOGGING
logDir = 'logs/'
if not os.path.exists(logDir):
    os.makedirs(logDir)
logging.basicConfig(filename= logDir + str(datetime.now()) + '.log',level=logging.INFO)

# Initialise the PCA9685, if cant use a dummy (for testing on machine that is not pi)
try:
  pwm = PCA9685.PCA9685()
except:
  msg = "WARNING - unable to load PWM chip... no values will set!"
  logging.info(msg)
  print(msg)
  pwm = PCA9685_dummy.PCA9685()









w, h = 16, 24
Matrix = [[0 for x in range(w)] for y in range(h)]

for x in range(w):
  Matrix[ 8][x] = 0 #8AM
  Matrix[ 9][x] = 0
  Matrix[10][x] = 0
  Matrix[11][x] = 0
  Matrix[12][x] = 0
  Matrix[13][x] = 10 #01PM
  Matrix[14][x] = 30
  Matrix[15][x] = 30
  Matrix[16][x] = 80
  Matrix[17][x] = 100 #05PM
  Matrix[18][x] = 100
  Matrix[19][x] = 100
  Matrix[20][x] = 80
  Matrix[21][x] = 50 #9PM
  Matrix[22][x] = 0
  Matrix[23][x] = 0



# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)



# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)


# Configure min and max, initial weather pattern
led_max = 4095  # Max Brightness
led_min = 0     # Min Brightness (off)
run = True
weather = WeatherType.normal






# Set frequency to 60hz for servos / 1000hz LEDS.
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
      thunderstorm_worker(channel, cur)


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


  for x in range(2):
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

                                         # ...Wait 0.9 seconds before starting another
except KeyboardInterrupt:
  logging.info(datetime.now().strftime('%H:%M:%S') +' : KeyboardInterrupt Quit')
  run = False
  pwm.set_all(led_min)


finally:
  logging.info(datetime.now().strftime('%H:%M:%S') +' : finally Quit')
  run = False
  pwm.set_all(led_min)
  os.unlink(pidfile)
  
