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

        while not self.cancelled:

            self.curTime = datetime.now()
            self.curHour = self.curTime.hour
            self.nextHour = (self.curTime + timedelta(hours=1)).hour
            self.goal = self.ls.get_pwm(self.c_id, self.nextHour)

            # nextPwm = round(self.goal * ( (self.curTime.minute * 60 + self.curTime.second) / 3600))

            lastGoal = self.ls.get_pwm(self.c_id, self.curHour)
            newGoal = self.goal
            newGoalWeight = (self.curTime.minute * 60 + self.curTime.second) / 3600
            lastGoalWeight = 1 - newGoalWeight
            currentTimeGoal = round((lastGoal * lastGoalWeight) +
                                    (newGoal * newGoalWeight))
            self.smoothTransition(currentTimeGoal)

            if (self.ls.get_preview_status(self.c_id)):
                self.preview_worker()

            if (s.weather == "storm"):
                self.thunderstorm_worker()

            if (s.weather == "cloudy"):
                self.new_cloud_worker()

            time.sleep(self.sleepTime)
            s.read_file()

    def cancel(self):
        """End this timer thread"""
        self.cancelled = True
        time.sleep(.2)

    def broadcast(self):

        self.sendInfo['c_id'] = self.c_id
        self.sendInfo['cur'] = self.cur
        self.sendInfo['goal'] = self.goal
        self.sendInfo['sleepTime'] = self.sleepTime
        self.sendInfo['delta'] = self.delta
        self.sendInfo['percent'] = round((self.cur / LED_MAX * 100))
        self.sendInfo['weather'] = s.weather
        self.sendInfo['alias'] = self.ls.get_alias(self.c_id)
        return self.sendInfo

    def preview_worker(self):
        timeout_length_secs = s.preview_timeout
        total_time_secs = 0

        print("Preview started on channel {:d}...timeout {:d}".format(
            self.c_id, timeout_length_secs))

        while (self.ls.get_preview_status(self.c_id)
               and total_time_secs < timeout_length_secs):
            self.smoothTransition(self.ls.get_preview_pwm(self.c_id))
            time.sleep(self.sleepTime)
            total_time_secs += self.sleepTime

        print("Preview ended on channel {:d}...total time {:d}".format(
            self.c_id, total_time_secs))
        self.ls.set_preview_status(self.c_id)



    def new_cloud_worker(self):
        speed = s.clouds_dim_speed
        while s.weather == "cloudy" and not self.cancelled:
            if self.ls.get_iswhite(self.c_id):
                speed = random.randint(2,10)
                light_peak = random.randint(LED_MIN + 25, LED_MAX )
                self.smoothTransition(light_peak, speed)
            else:   #dim colored lights to something
                self.smoothTransition(100, _speed=2)
                
            time.sleep(1)
            s.weather='normal'
            s.dump_file()
    def thunderstorm_worker(self):
        '''makes a thunderstorm'''

        self.smoothTransition(LED_MIN) #always fade to nothing at end
        time.sleep(5)

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

            if not self.ls.get_iswhite(self.c_id):  #dont do lightning stikes
                r_pwm = random.randint(1, 200)  #TODO magicnumber
                self.smoothTransition(r_pwm)
                time.sleep(random.uniform(0, 2))

            else:  # do lightning strikes
                if (random.randint(1, 5) == 3):
                    self.setPwm(LED_MIN)
                    time.sleep(random.uniform(0, 1))
                    self.setPwm(LED_MAX)
                    time.sleep(random.uniform(0, .02))
                    print(datetime.now().strftime('%H:%M:%S') + "|Channel = " +
                          str(self.c_id) + "|Lightning Strike!")

                    if random.randint(1, 5) == 2:
                        x = 0
                        r = random.randint(-200, 200)
                        y = random.randint(100, 2000)
                        while (x < y):
                            r = random.randint(-100, 200)
                            self.setPwm(x)
                            x = x + r
                            self.setPwm(LED_MIN)
                            time.sleep(random.uniform(0, .09))

                        time.sleep(random.uniform(0, 4))
        
        self.smoothTransition(LED_MIN) #always fade to nothing at end
        time.sleep(5)

    def setPwm(self, pwmval):
        '''sets pwm and value to hold it'''
        if pwmval > LED_MAX or pwmval < LED_MIN:
            logger.info("PWM value is out of range =" + str(pwmval))
        pwmval = max(pwmval, LED_MIN)
        pwmval = min(pwmval, LED_MAX)
        self.cur = pwmval
        self.pwm.set_s(self.c_id, pwmval)
        logger.debug("set pwm to" + str(pwmval))
        return self.cur
    
    def smoothTransition(self, _end=0, _speed=1):
        '''runs to smooth transitions'''
        _start = self.cur

        if not abs(_start - _end) > 1:
            logger.debug("Channel %s - Transition started - Start=%s End=%s Speed=%s",
                        self.c_id, _start, _end, _speed)

        if _start > _end:
            _speed = _speed * -1

        for pwm in range(_start, _end, _speed):
            self.setPwm(pwm)

        self.setPwm(_end) #ensure always get to end
