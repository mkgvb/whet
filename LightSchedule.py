import json
import os
import logging
import random

FILELOC = 'json/schedule.json'

HOURS = 24
LED_MAX = 4095
LED_MIN = 0
LOGGER = logging.getLogger('__main__')


class LightSchedule(dict):
    """Class to hold lighting schedule"""

    last_access_time = 0

    def __init__(self, *args, **kwargs):
        super(LightSchedule, self).__init__(*args, **kwargs)
        self.__dict__ = self

        if not os.path.isfile(FILELOC):
            self.default()
            self.set_data()

    def default(self):
        channels = []
        for j in range(random.randint(1,14)):
            channel = {}
            schedule = []

            preview = {}
            preview["active"] = False
            preview["value"] = 0
            channel['preview'] = preview
            channel['iswhite'] = bool(random.getrandbits(1))
            

            channel['id'] = j
            channel['color'] = '#' + str(random.randint(0, 999999))

            for i in range(0, 24):
                dp = {}
                dp['hour'] = i
                dp['percent'] = random.randint(0, 100)
                schedule.append(dp)
            channel['schedule'] = schedule

            channels.append(channel)

        self.data = {}
        self.data["channels"] = channels

        # for i in range(5):
        #     self.data['channels'][i] = { id =i}
        print(json.dumps(self.data, indent=4))

    def get_data(self):
        """gets a current copy of the schedule if it has changed"""
        valid_read = False
        if self.last_access_time != os.stat(FILELOC).st_mtime:
            self.last_access_time = os.stat(FILELOC).st_mtime
            while not valid_read:
                try:
                    with open(FILELOC) as data_file:
                        self.data = json.load(data_file)
                        LOGGER.info("Channel Schedule Changed " +
                                    str(os.stat(FILELOC).st_mtime))
                        valid_read = True

                except:
                    LOGGER.exception("Thread File Read Failed!!! - FIX THIS")

        return self.data['channels']

    def set_data(self):
        "sets a value in the file"
        with open(FILELOC, 'w') as data_file:
            data_file.write(json.dumps(
                self.data, default=lambda o: o.__dict__, sort_keys=True, indent=4))

    def get_percent(self, channel, hour):
        """gets percentage value from schedule"""
        data = self.get_data()
        for obj in data:
            if obj['id'] == channel:
                for obj2 in obj['schedule']:
                    if obj2['hour'] == hour:
                        return min(100, max(int(obj2['percent']), 0))

        LOGGER.error("Hour=%s Channel=%s Something went wrong getting percent", hour, channel)
        return 0

    def get_percent_cur(self, pwm_val):
        '''gets percent value of pwm_val'''
        return int(round((pwm_val / LED_MAX) * 100, 1))

    def get_pwm(self, channel, hour):
        """gets the pwm value of a channel at a certain hour"""
        return int(round((self.get_percent(channel, hour) / 100) * LED_MAX))

    def get_preview_pwm(self, channel):
        """gets pwm value of preview"""
        data = self.get_data()
        for obj in data:
            if obj['id'] == channel:
                return obj['preview']['value']

    def get_preview_status(self, channel):
        """gets preview status"""
        data = self.get_data()
        for obj in data:
            if obj['id'] == channel:
                return obj['preview']['active']

    def get_iswhite(self, channel):
        data = self.get_data()
        if 'lightning' in data[channel]:
            return data[channel]['lightning']
        elif 'iswhite' in data[channel]:
            return data[channel]['iswhite']
        else:
            data[channel]['iswhite'] = False
            self.set_data()
            
        return False


    def set_preview_status(self, channel, status=False):
        """sets preview status"""
        data = self.get_data()
        for obj in data:
            if obj['id'] == channel:
                obj['preview']['active'] = status
        self.set_data()

    def get_number_of_channels(self):
        """gets total number of active channels"""
        data = self.get_data()
        cnt = 0
        for obj in data:
            cnt += 1
        return cnt
