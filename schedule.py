<<<<<<< Updated upstream
# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
=======
#!/usr/bin/env python3

>>>>>>> Stashed changes
from __future__ import division
import time
from datetime import datetime
import random
import math
import logging
<<<<<<< Updated upstream
import Adafruit_PCA9685


logging.basicConfig(filename= 'logs/' + str(datetime.now()) + '.log',level=logging.INFO)
=======
import threading
import os
from weatherType import WeatherType
import PCA9685
import sys



logDir = 'logs/'
if not os.path.exists(logDir):
    os.makedirs(logDir)
logging.basicConfig(filename= logDir + str(datetime.now()) + '.log',level=logging.INFO)

pid = str(os.getpid())
pidfile = "/tmp/whet.pid"

if os.path.isfile(pidfile):
    logging.info("%s already exists, exiting" % pidfile)
    print("%s already exists, exiting" % pidfile)
    sys.exit()
open(pidfile, 'w').write(pid)



>>>>>>> Stashed changes


w, h = 16, 24;
Matrix = [[0 for x in range(w)] for y in range(h)] 

for x in range(w):
  Matrix[11][x] = 00 #11AM 
  Matrix[12][x] = 00
  Matrix[13][x] = 00
  Matrix[14][x] = 30
  Matrix[15][x] = 50
  Matrix[16][x] = 70
  Matrix[17][x] = 100
  Matrix[18][x] = 100
  Matrix[19][x] = 50 
  Matrix[20][x] = 10
  Matrix[21][x] = 00 #9PM

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

<<<<<<< Updated upstream
# Configure min and max servo pulse lengths
dim_min = 0  # Min pulse length out of 4096
dim_max = 4095   # Max pulse length out of 4096

# Helper function to make setting a servo pulse width simpler.
=======

# Configure min and max brightness values
dim_min = 0  # Min pulse length out of 4096
dim_max = 4095   # Max pulse length out of 4096


#if set to false threads kill themselves
run = True

#default weather
weather = WeatherType.normal

>>>>>>> Stashed changes


# Initialise the PCA9685 using the default address (0x40).
pwm = PCA9685.PCA9685()


# Set frequency to 1000hz for LEDS.
pwm.set_pwm_freq(1000)
pwm.set_all_pwm( 0, dim_max)
time.sleep(1)





def percent(percent):
        if (percent == 0):
         return dim_max
        if (percent == 100):
         return dim_min

        percent = percent / 100
        return int(dim_max - dim_max * percent)


#time
curHour = datetime.now().hour
cur = dim_max
<<<<<<< Updated upstream
=======
def channel_worker(channel):
  print(timeStr(datetime.now()) + '|Channel = {0}| Starting main...  '.format(channel) )
  cur = dim_max
  while run:



    curTime = datetime.now()
    nextHour = curTime + timedelta(hours=1)
    curHour = curTime.hour
    goal = percent(Matrix[(nextHour.hour)][channel]);
    remainSeconds = 3600 - (curTime.minute * 60 + curTime.second)
    delta = abs(cur - goal)
    sleepTime = int(remainSeconds / delta ) if delta != 0 else 60

    print( timeStr(curTime)
      + "|Channel = {0}".format(channel)
      + "|Hour = {0}".format(curHour)
      + "|Goal = {0}({1}%)".format(goal, toBrightnessPercent(goal))
      + "|Cur = " + str(cur) + "(" + str(toBrightnessPercent(cur)) + "%)"
      + "|Sleep = " + str(sleepTime)
      + "|Delta = " + str(delta)
      + "|Seconds Remain = " + str(remainSeconds))

    logging.info( timeStr(curTime)
      + "|Channel = " + str(channel)
      + "|Hour = " + str(curHour)
      + "|Goal = "+ str(goal) + "(" + str(toBrightnessPercent(goal)) + "%)"
      + "|Cur = " + str(cur) + "(" + str(toBrightnessPercent(cur)) + "%)"
      + "|Sleep = " + str(sleepTime)
      + "|Delta = " + str(delta)
      + "|Seconds Remain = " + str(remainSeconds))

    if (cur > goal ):
      cur -= 1 ;
    if (cur < goal):
      cur += 1;

>>>>>>> Stashed changes


def timeStr():
  return datetime.now().strftime('%H:%M:%S')


def catchup(cur):
  print(datetime.now().strftime('%H:%M:%S') + ' : Starting catchup...')
  while cur < percent(Matrix[curHour][0]):
    cur += 1;
    print(str(cur))
    pwm.set_pwm(0,0,cur)
    time.sleep(.009);
  while cur > percent(Matrix[curHour][0]):
    cur -= 1;
    print(str(cur))
    pwm.set_pwm(0,0,cur)
  print(datetime.now().strftime('%H:%M:%S') + ' : Finished catchup...')
  return cur

def main(cur):
  print(datetime.now().strftime('%H:%M:%S') + ' : Starting main...')
  while True:
    
    goal = percent(Matrix[datetime.now().hour+1][0]);

<<<<<<< Updated upstream
    print("Hour = " + str(datetime.now().hour) + " | " + "Goal = "+ str(goal) + " | " + "Cur = " + str(cur))
  	
    if (cur > goal ):
   	cur -= 1 ;
    if (cur < goal):
    	cur += 1;

    #set 
    pwm.set_pwm(0,0,cur)

    if cur == goal:
      time.sleep(30)
      print("hour = " +str(datetime.now().hour) +"   cur = " + str(cur) + " " + str(Matrix[datetime.now().hour][0]) +"%")
    else:
      print("hour = " +str(datetime.now().hour))
      print(str(cur))
      time.sleep((3600 - datetime.now().minute * 60 + datetime.now().second) / abs(cur - goal) )
      print("Sleeping " + str((3600 - datetime.now().minute * 60 + datetime.now().second) / abs(cur - goal)) + " Seconds")
      print ("Seconds left in job:" + str(3600 - (datetime.now().minute * 60 + datetime.now().second)))
  return cur


=======
def thunderstorm_worker(channel, cur):
  while (weather == WeatherType.storm and run):

    #dim to percentage of normal weather
    #TODO
    tmpPwm = dim_min


    if (random.randint(1,5) == 3):

      pwm.set_pwm(channel, 0, dim_max)
      time.sleep(random.uniform(0, 1))  #valley

      pwm.set_pwm(channel, 0, dim_min)
      time.sleep(random.uniform(0, .02))  #peak

      
      if (random.randint(1, 5) == 3):
        while tmpPwm > dim_max:
          tmpPwm -= 10
          pwm.set_pwm(channel, 0, tmpPwm) #quick ramp down effect

      print( timeStr(datetime.now())
        + "|Channel = " + str(channel)
        + "|Lightning Strike!")
>>>>>>> Stashed changes



try:
  cur = catchup(cur)
  cur = main(cur)
except KeyboardInterrupt:
  logging.debug(datetime.now().strftime('%H:%M:%S') +' : Quitting')
  pwm.set_pwm(0,0,dim_max)



