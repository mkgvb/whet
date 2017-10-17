import json
import math
import os
import logging

fileloc = 'json/schedule.json'

HOURS = 24
LED_MAX= 4095
LED_MIN= 0

class LightSchedule(object):
    """Class to hold lighting schedule"""

    # def __init__(self):
    #     pass:
    last_access_time = 0
    data = None


    def get_data(self):
        """gets a current copy of the schedule if it has changed"""
        valid_read = False
        if self.last_access_time != os.stat(fileloc).st_mtime:
            self.last_access_time = os.stat(fileloc).st_mtime
            while not valid_read:
                try:
                    with open(fileloc) as data_file:
                        self.data = json.load(data_file)
                        logging.info("Channel Schedule Changed " + str(os.stat(fileloc).st_mtime))
                        valid_read = True
                except:
                    logging.info("Thread File Read Failed!!! - FIX THIS")
                

        return self.data['channels']

    def set_data(self):
        "sets a value in the file"
        with open(fileloc, 'w') as data_file:
            data_file.write(json.dumps(
                self.data, default=lambda o: o.__dict__, sort_keys=True, indent=4))


    def get_percent(self, channel, hour):
        """gets percentage value from schedule"""
        data = self.get_data()
        r = 0
        for x in data:
            if (x['id'] == channel):
                for y in x['schedule']:
                    if (y['hour'] == hour):
                        r = int(y['percent'])

        if r == None:
            # why you no print?
            # i guess r := None just leaves it at 0
            logging.info("Something is wrong Asked for channel={0} hour={1} giving 0")
            return 0
        else:
            return min(100, max(r, 0))
        return

    def get_percent_cur(self, pwm_val):
        '''gets percent value of pwm_val'''
        return int(round((pwm_val / LED_MAX) * 100, 1))

    def get_pwm(self, channel, hour):
        """gets the pwm value of a channel at a certain hour"""
        return int(round((self.get_percent(channel, hour) / 100) * LED_MAX))

    def get_preview_pwm(self, channel):
        """gets pwm value of preview"""
        data = self.get_data()
        for x in data:
            if (x['id'] == channel):
                return x['preview']['value']

    def get_preview_status(self, channel):
        """gets preview status"""
        data = self.get_data()
        for x in data:
            if (x['id'] == channel):
                return x['preview']['active']

    def set_preview_status(self, channel, input=False):
        """sets preview status"""
        data = self.get_data()
        for x in data:
            if (x['id'] == channel):
                x['preview']['active'] = input
        self.set_data()



    def get_number_of_channels(self):
        """gets total number of active channels"""
        data = self.get_data()
        c = 0
        for x in data:
            c += 1
        return c
