# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
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
#import Adafruit_PCA9685

logDir = 'logs/'
if not os.path.exists(logDir):
    os.makedirs(logDir)
logging.basicConfig(filename= logDir + str(datetime.now()) + '.log',level=logging.INFO)


w, h = 16, 24;
Matrix = [[0 for x in range(w)] for y in range(h)] 

for x in range(w):
  Matrix[ 8][x] = 10 #8AM
  Matrix[ 9][x] = 0
  Matrix[10][x] = 100
  Matrix[11][x] = 50 
  Matrix[12][x] = 100
  Matrix[13][x] = 10 #01PM
  Matrix[14][x] = 90
  Matrix[15][x] = 30
  Matrix[16][x] = 80
  Matrix[17][x] = 40
  Matrix[18][x] = 70
  Matrix[19][x] = 0 
  Matrix[20][x] = 35
  Matrix[21][x] = 99 #9PM
  Matrix[22][x] = 1
  Matrix[23][x] = 42



# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)



# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)


# Configure min and max servo pulse lengths
dim_min = 0  # Min pulse length out of 4096
dim_max = 4095   # Max pulse length out of 4096
run = True
thunderstorm = False
# Helper function to make setting a servo pulse width simpler.


# Initialise the PCA9685 using the default address (0x40).
#pwm = Adafruit_PCA9685.PCA9685()


# Set frequency to 60hz for servos / 1000hz LEDS.
#pwm.set_pwm_freq(1000)
#pwm.set_all_pwm( 0, dim_max)
time.sleep(1)





def percent(percent):
  if (percent == 0):
   return dim_max
  if (percent == 100):
   return dim_min

  percent = percent / 100
  return int(dim_max - dim_max * percent)

def timeStr(t):
  return t.strftime('%H:%M:%S')

cur = dim_max
def channel_worker(channel):
  print(timeStr(datetime.now()) + ' : Starting main...')
  cur = dim_max
  while run:

    
    
    curTime = datetime.now()
    nextHour = curTime + timedelta(hours=1)
    curHour = curTime.hour
    goal = percent(Matrix[(nextHour.hour)][channel]);
    remainSeconds = 3600 - (curTime.minute * 60 + curTime.second)
    delta = abs(cur - goal)
    sleepTime = int(remainSeconds / delta ) if delta != 0 else 1

    print( timeStr(curTime)
      + "|Channel = " + str(channel) 
      + "|Hour = " + str(curHour) 
      + "|Goal = "+ str(goal) 
      + "|Cur = " + str(cur) 
      + "|Sleep = " + str(sleepTime) 
      + "|Delta = " + str(delta)
      + "|Seconds Remain = " + str(remainSeconds))
    
    if (cur > goal ):
      cur -= 1 ;
    if (cur < goal):
      cur += 1;

    #set 
    #pwm.set_pwm(channel,0,cur)
    time.sleep(sleepTime)

    if (thunderstorm):
      thunderstorm_worker(channel)



def thunderstorm_worker(channel):
  while (thunderstorm and run):
    #pwm.set_pwm(channel, 0, dim_max)
    time.sleep(random.uniform(0, 1))
    #pwm.set_pwm(channel, 0, dim_min)
    time.sleep(random.uniform(0, .002))
    print( timeStr(datetime.now())
      + "|Channel = " + str(channel) 
      + "|Lightning Strike!")

try:

  threads = []


  '''
  for x in range(2):
    print(x)                                     # Four times...
    t = threading.Thread(target=thunderstorm_worker, args=(x,))
    threads.append(t)
    t.start()                                   # ...Start the thread
    time.sleep(.5)
    '''

  for x in range(2):
    print(x)                                     # Four times...
    t = threading.Thread(target=channel_worker, args=(x,))
    threads.append(t)
    t.start()                                   # ...Start the thread
    time.sleep(2)
    

  #keep main thread alive
  while True:
    time.sleep(1)
    print("thunderstorm = " + str(thunderstorm))
    #if (datetime.now().hour > 21):
    if (random.randint(1,10) == 5):
      thunderstorm = True
      stormLength = random.randint(100,500)
      print(timeStr(datetime.now()) + ' : Starting thunderstorm... Length = '+ str(stormLength))
      time.sleep(stormLength)
    thunderstorm = False

                                         # ...Wait 0.9 seconds before starting another
except KeyboardInterrupt:
  print("Stopping Threads")
  logging.debug(datetime.now().strftime('%H:%M:%S') +' : Quitting')
  run = False
  #pwm.set_all_pwm(0, dim_max)
