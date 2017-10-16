from threading import Thread
import logging
import time
from datetime import datetime, timedelta
import random
import json

from WeatherType import WeatherType
import LightSchedule
import Settings
from websocket import create_connection

ws = create_connection("ws://localhost:8080/chat/websocket")
s = Settings.Settings()
LED_MIN=0
LED_MAX=4095

class Channel(Thread):
    


    def __init__(self, c_id, pwm, channel_info):
        super(Channel, self).__init__(name=str(c_id))
        self.daemon = True
        self.cancelled = False

        # do other initialization here
        self.ls = channel_info
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
            self.goal = self.ls.get_pwm(self.c_id, self.nextHour)
            self.remainSeconds = 3600 - (self.curTime.minute * 60 + self.curTime.second)
            self.delta = abs(self.cur - self.goal)
            self.sleepTime = int(self.remainSeconds / self.delta) if self.delta != 0 else 1


            #if self.delta > 2000 and self.cur < self.goal:
            #    self.catchup_worker()


            msg = ""
            msg += self.curTime.strftime('%H:%M:%S')
            msg += "|Channel = " + str(self.c_id)
            msg += "|Hour = " + str(self.curHour)
            msg += "|Cur = " + str(self.cur)
            msg += "|Goal = " + str(self.goal)
            msg += "|Sleep = " + str(self.sleepTime)
            msg += "|Delta = " + str(self.delta)
            msg += "|Seconds Remain = " + str(self.remainSeconds)

            logging.debug(msg)

            if (self.cur > self.goal):
                self.cur -= 1
            if (self.cur < self.goal):
                self.cur += 1


            if (self.ls.get_preview_status(self.c_id)):
                self.preview_worker()

            if (s.weather == "storm"):
                self.thunderstorm_worker()

            if (s.weather == "cloudy"):
                self.cloud_worker()

            # happy path
            # set
            self.pwm.set_s(self.c_id, self.cur)
            time.sleep(self.sleepTime)

            if (self.sleepTime > 0):
                self.broadcast()
            
      

    def cancel(self):
        """End this timer thread"""
        self.cancelled = True

    def update(self):
        """Update the counters"""
        print("running thread class!")

    def broadcast(self):


        obj = {}
        obj['c_id'] = self.c_id
        obj['cur'] = self.cur
        obj['goal'] = self.goal
        obj['sleepTime'] = self.sleepTime
        obj['delta'] = self.delta
        obj['percent'] = round((self.cur / LED_MAX * 100))

        ws.send(
            '{"channel":'
            + json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)
            + '}'
        )
        
       
    def preview_worker(self):
        timeout_length_secs = 300
        total_time_secs = 0
        cur_init = self.cur
        cur_local = 0
        print("Preview started on channel {:d}...timeout {:d}".format(self.c_id, timeout_length_secs))
        while(self.ls.get_preview_status(self.c_id) and total_time_secs < timeout_length_secs):
            self.cur = self.ls.get_preview_pwm(self.c_id)
            if cur_local != self.cur:
                self.pwm.set_s(self.c_id, self.cur)
                cur_local = self.cur
                print("Preview value changed to {:d} on channel {:d}".format(cur_local, self.c_id ))
            self.broadcast()
            time.sleep(self.sleepTime)
            total_time_secs += self.sleepTime
        print("Preview ended on channel {:d}...total time {:d}".format(self.c_id, total_time_secs))
        self.cur = cur_init
        self.ls.set_preview_status(self.c_id)
        

    def catchup_worker(self):
        
        catchup_time= s.catchup_time
        catchup_steps = s.catchup_steps

        curTime = datetime.now()
        curHour = curTime.hour
        nextHour = (curTime + timedelta(hours=1)).hour
        curGoal = self.ls.get_pwm(self.c_id, curHour)
        nextGoal = self.ls.get_pwm(self.c_id, nextHour)
        catchup_delta = nextGoal - curGoal
        catchupGoal = curGoal + catchup_delta * (curTime.minute / 60)

        # catchup - idealy runs once unless something is wrong
        i = 0
        while i <= catchup_steps:
            self.cur += round(catchupGoal / catchup_steps)
            self.pwm.set_s(self.c_id, self.cur)
            time.sleep(catchup_time / catchup_steps)
            print(i)
            i += 1

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
                logging.info("Cant play thunderstorm audio")
        while (s.weather == "storm"):

            # dim to percentage of normal weather
            # TODO

            if (random.randint(1, 5) == 3):
                self.pwm.set_s(self.c_id, LED_MIN)
                time.sleep(random.uniform(0, 1))
                self.pwm.set_s(self.c_id, LED_MAX)
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
                        self.pwm.set_s(self.c_id, LED_MIN)
                        time.sleep(random.uniform(0, .09))

                    time.sleep(random.uniform(0, 4))



# my_class_instance = MyClass()

# # explicit start is better than implicit start in constructor
# my_class_instance.start()

# # you can kill the thread with
# my_class_instance.cancel()