from threading import Thread
import logging
import time
from datetime import datetime, timedelta
import random

import Settings

s = Settings.Settings()
LED_MIN = 0
LED_MAX = 4095
logger = logging.getLogger('__main__')


class Channel(Thread):

    def __init__(self, c_id, pwm, channel_info):
        super(Channel, self).__init__(name=str(c_id))
        self.daemon = True
        self.cancelled = False

        # do other initialization here
        self.ls = channel_info
        self.pwm = pwm
        self.c_id = c_id
        self.curTime = datetime.now()
        self.cur = 0
        self.goal = 0
        self.sleepTime = 1
        self.delta = 0
        self.weather = 'null'
        
        self.sendInfo = {}

        #self.weather = Settings.Settings().weather

    def run(self):
        """Overloaded Thread.run"""
        time.sleep(self.c_id)
        self.transition_worker()

        while not self.cancelled:

            self.dead = self.cancelled

            self.curTime = datetime.now()
            self.curHour = self.curTime.hour
            self.nextHour = (self.curTime + timedelta(hours=1)).hour
            self.goal = self.ls.get_pwm(self.c_id, self.nextHour)
            self.remainSeconds = 3600 - \
                (self.curTime.minute * 60 + self.curTime.second)
            self.delta = abs(self.cur - self.goal)
            self.sleepTime = 1

            nextPwm = round(self.goal * ( (self.curTime.minute * 60 + self.curTime.second) / 3600))
            self.cur = round((self.cur * .8) + (nextPwm * .2))
            self.pwm.set_s(self.c_id, self.cur)


            if (self.ls.get_preview_status(self.c_id)):
                self.preview_worker()

            if (s.weather == "storm"):
                self.thunderstorm_worker()

            if (s.weather == "cloudy"):
                self.cloud_worker()


            
                


            time.sleep(self.sleepTime)
            s.read_file()


    def cancel(self):
        """End this timer thread"""
        self.cancelled = True
        time.sleep(.2)

    def update(self):
        """Update the counters"""
        print("running thread class!")

    def broadcast(self):

        self.sendInfo['c_id'] = self.c_id
        self.sendInfo['cur'] = self.cur
        self.sendInfo['goal'] = self.goal
        self.sendInfo['sleepTime'] = self.sleepTime
        self.sendInfo['delta'] = self.delta
        self.sendInfo['percent'] = round((self.cur / LED_MAX * 100))
        self.sendInfo['weather'] = s.weather
        return self.sendInfo

    def preview_worker(self):
        timeout_length_secs = s.preview_timeout
        sleep_interval = 1
        total_time_secs = 0
        cur_init = self.ls.get_preview_pwm(self.c_id)
        cur_init_new = cur_init
        print("Preview started on channel {:d}...timeout {:d}".format(
            self.c_id, timeout_length_secs))

        self.transition_worker(_start=self.cur, _end=cur_init_new, _usetime=False)
        print("Preview value changed to {:d} on channel {:d}".format( cur_init_new, self.c_id))
        while(self.ls.get_preview_status(self.c_id) and total_time_secs < timeout_length_secs):
            if cur_init_new != self.ls.get_preview_pwm(self.c_id):
                cur_init_new =  self.ls.get_preview_pwm(self.c_id)
                self.transition_worker(_start=cur_init, _end=cur_init_new, _usetime=False)
                cur_init = cur_init_new

            time.sleep(sleep_interval)
            total_time_secs += sleep_interval
        print("Preview ended on channel {:d}...total time {:d}".format(
            self.c_id, total_time_secs))
        self.ls.set_preview_status(self.c_id)
        self.transition_worker(_start=cur_init_new)

    def transition_worker(self, _start=0, _end=0, _usetime=True):
        '''runs at the begining of channel thread creation to catch it up to where brightness should be'''

        if _usetime:
            catchup = round(abs((self.ls.get_pwm(self.c_id, self.curTime.hour) -
                                 self.ls.get_pwm(self.c_id, self.curTime.hour + 1)) * (self.curTime.minute / 60)))
            trans_goal = min(self.ls.get_pwm(self.c_id, self.curTime.hour), self.ls.get_pwm(
                self.c_id, self.curTime.hour + 1)) + catchup
        else:
            trans_goal = _end

        i = _start
        logger.info("Channel %s - Transition started - Start=%s End=%s",
                    self.c_id, _start, trans_goal)
        while i < trans_goal:
            i += 1
            self.pwm.set_s(self.c_id, i)
        while i > trans_goal:
            self.pwm.set_s(self.c_id, i)
            i -= 1
        self.cur = i

    def cloud_worker(self):
        '''makes a cloud'''

        dim_percent = s.clouds_dim_percent
        dim_resolution = s.clouds_dim_resolution
        dim_speed = s.clouds_dim_speed
        init_cur = self.cur

        print("{} Cloud Coverage begin channel {} : Cur = {}".format(
            datetime.now(), self.c_id, self.cur))
        dim_to = round(self.cur * dim_percent)
        dim_interval = round(self.cur / dim_resolution)

        while not self.cancelled:
            while self.cur > dim_to and s.weather == "cloudy":
                self.cur -= dim_interval
                self.pwm.set_s(self.c_id, self.cur)
                time.sleep(dim_speed)
            while self.cur < init_cur:
                self.cur += dim_interval
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
            except ImportError:
                logger.info(
                    "Cant import SimpleAudio / play thunderstorm audio")

        while s.weather == "storm" and not self.cancelled:
            s.read_file()

            if not self.ls.get_lightning(self.c_id):    #dont do lightning stikes
                    r_pwm = random.randint(1,200)   #TODO magicnumber
                    self.transition_worker(self.cur, r_pwm, False)
                    self.cur = r_pwm
                    time.sleep(random.uniform(0, 2))

            else:   # do lightning strikes
                if (random.randint(1, 5) == 3):
                    self.pwm.set_s(self.c_id, LED_MIN)
                    time.sleep(random.uniform(0, 1))
                    self.pwm.set_s(self.c_id, LED_MAX)
                    time.sleep(random.uniform(0, .02))
                    print(datetime.now().strftime('%H:%M:%S')
                        + "|Channel = " + str(self.c_id)
                        + "|Lightning Strike!")

                    if random.randint(1, 5) == 2:
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


        self.transition_worker(_start=self.cur, _usetime=True)
