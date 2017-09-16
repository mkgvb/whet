# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
import time
from datetime import datetime
import random
# Import the PCA9685 module.
import Adafruit_PCA9685


# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
dim_min = 0  # Min pulse length out of 4096
dim_max = 4095   # Max pulse length out of 4096

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(1000)



#time
curTime = datetime.now().strftime('%H:%M')

cur = dim_min
print(curTime + ' : Thunder Storm Starting...')
while True:
    # Move servo on channel O between extremes.
    #print(curTime)
    
    #pwm.set_pwm(0, 0, servo_min)
    #time.sleep(.5)
    #pwm.set_pwm(0, 0, 2000)
    #time.sleep(.01)
    
  pwm.set_pwm(0, 0, dim_max)
  time.sleep(random.uniform(0, 1))
  pwm.set_pwm(0, 0, 0)
  time.sleep(random.uniform(0, .05))

    #while cur < dim_max:
    # pwm.set_pwm(0, 1000, 0)
    # cur = cur + 1

    #print(str(cur) + " Is current... waiting")
    #time.sleep(5)

    #while cur > dim_min:
	# pwm.set_pwm(0, 0, 0)
	# cur = cur - 1
 

