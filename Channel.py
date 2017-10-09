from threading import Thread

import time
from datetime import datetime, timedelta
import random
import json

from WeatherType import WeatherType
import LightSchedule
import Settings
import wsclient

s = Settings.Settings()
ws = wsclient

class Channel(Thread):
    LED_MIN=0
    LED_MAX=4095
    


    def __init__(self, c_id, pwm):
        super(Channel, self).__init__()
        self.daemon = True
        self.cancelled = False

        # do other initialization here
        self.pwm = pwm
        self.c_id = c_id
        self.cur = 0
        self.curTime = datetime.now()
        #self.weather = Settings.Settings().weather


    def run(self):
        """Overloaded Thread.run"""

        while not self.cancelled:
            self.curTime = datetime.now()
            self.curHour = self.curTime.hour
            self.nextHour = (self.curTime + timedelta(hours=1)).hour
            self.goal = LightSchedule.LightSchedule().get_pwm(self.c_id, self.nextHour)
            self.remainSeconds = 3600 - (self.curTime.minute * 60 + self.curTime.second)
            self.delta = abs(self.cur - self.goal)
            self.sleepTime = int(self.remainSeconds / self.delta) if self.delta != 0 else 1

            if self.cur < LightSchedule.LightSchedule().get_pwm(self.c_id, self.curHour):
                self.catchup_worker()


            msg = ""
            msg += self.curTime.strftime('%H:%M:%S')
            msg += "|Channel = " + str(self.c_id)
            msg += "|Hour = " + str(self.curHour)
            msg += "|Cur = " + str(self.cur)
            msg += "|Sleep = " + str(self.sleepTime)
            msg += "|Delta = " + str(self.delta)
            msg += "|Seconds Remain = " + str(self.remainSeconds)

            print(msg)

            if (self.cur > self.goal):
                self.cur -= 1
            if (self.cur < self.goal):
                self.cur += 1

            if (s.weather == "storm"):
                self.thunderstorm_worker()

            if (s.weather == "cloudy"):
                self.cloud_worker()

            # happy path
            # set
            self.pwm.set_s(self.c_id, self.cur)
            self.broadcast()
            time.sleep(self.sleepTime)
            
      

    def cancel(self):
        """End this timer thread"""
        self.cancelled = True

    def update(self):
        """Update the counters"""
        print("running thread class!")

    def broadcast(self):

        obj = {}
        obj['cur'] = self.cur
        obj['c_id'] = self.c_id
        ws.send(
            '{"channel":'
            + json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)
            + '}'
        )
            
        

    def catchup_worker(self):
        
        catchup_steps = s.catchup_steps
        catchup_time= s.catchup_time

        curTime = datetime.now()
        curHour = curTime.hour
        nextHour = (curTime + timedelta(hours=1)).hour
        curGoal = LightSchedule.LightSchedule().get_pwm(self.c_id, curHour)
        nextGoal = LightSchedule.LightSchedule().get_pwm(self.c_id, nextHour)
        catchup_delta = nextGoal - curGoal
        catchupGoal = curGoal + catchup_delta * (curTime.minute / 60)

        # catchup - idealy runs once unless something is wrong
        while self.cur < catchupGoal:
            self.cur += round(self.goal / catchup_steps)
            self.pwm.set_s(self.c_id, self.cur)
            time.sleep(catchup_time / catchup_steps)
            print(self.cur)

    def cloud_worker(self):
        '''makes a cloud'''

        dim_percent = s.clouds_dim_percent
        dim_resolution = s.clouds_dim_resolution
        dim_speed = s.clouds_dim_speed
        init_cur = self.cur

        print("{} Cloud Coverage begin channel {} : Cur = {}".format(datetime.now(), self.c_id, self.cur))
        dimTo = round(self.cur * dim_percent)
        dimInterval = round(self.cur / dim_resolution)

        while not self.cancelled:
            while self.cur > dimTo and s.weather == "cloudy":
                self.cur -= dimInterval
                self.pwm.set_s(self.c_id, self.cur)
                time.sleep(dim_speed)
            while self.cur < init_cur:
                self.cur += dimInterval
                self.pwm.set_s(self.c_id, self.cur)
                time.sleep(dim_speed)

    def thunderstorm_worker(self):
        '''makes a thunderstorm'''

        if s.sound_on and self.c_id == 0:
            try:
                import simpleaudio as sa
                wave_obj = sa.WaveObject.from_wave_file("sound/t1.wav")
                # wave_obj = sa.WaveObject.from_wave_file("sound/t" + str(random.randint(1, 5)) + ".wav")
                play_obj = wave_obj.play()
            except:
                print("Cant play thunderstorm audio")
        while (s.weather == "storm"):

            # dim to percentage of normal weather
            # TODO

            if (random.randint(1, 5) == 3):
                self.pwm.set_s(self.c_id, self.LED_MIN)
                time.sleep(random.uniform(0, 1))
                self.pwm.set_s(self.c_id, self.LED_MAX)
                time.sleep(random.uniform(0, .02))
                print(datetime.now().strftime('%H:%M:%S')
                    + "|Channel = " + str(self.c_id)
                    + "|Lightning Strike!")

                if (random.randint(1, 5) == 2):
                    x = 0
                    r = random.randint(-200, 200)
                    y = random.randint(100, 2000)
                    while (x < y):
                        r = random.randint(-100, 200)
                        self.pwm.set_s(self.c_id, x)
                        x = x + r
                        self.pwm.set_s(self.c_id, self.LED_MIN)
                        time.sleep(random.uniform(0, .09))

                    time.sleep(random.uniform(0, 4))



# my_class_instance = MyClass()

# # explicit start is better than implicit start in constructor
# my_class_instance.start()

# # you can kill the thread with
# my_class_instance.cancel()