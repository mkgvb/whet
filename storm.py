import random
import time
import whet

def thunderstorm_worker(pwm, channel, cur):

    #TODO Sound

    #dim to percentage of normal weather
    #TODO


    if (random.randint(1,5) == 3):
      pwm.set_s(channel, whet.led_min)
      time.sleep(random.uniform(0, 1))
      pwm.set_s(channel, whet.led_max)
      time.sleep(random.uniform(0, .02))
      #print( timeStr(datetime.now())
      #  + "|Channel = " + str(channel)
      #  + "|Lightning Strike!")

      if (random.randint(1,5) == 2):
        x = 0
        r = random.randint(-200,200)
        y = random.randint(100,2000)
        while (x < y):
          r = random.randint(-100,200)
          pwm.set_s(channel, x)
          x = x+r
          pwm.set_s(channel, whet.led_min)
          time.sleep(random.uniform(0, .09))

        time.sleep(random.uniform(0, 4))