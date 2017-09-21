import json
import math
#import Settings
import Settings2

fileloc = 'json/schedule.json'


HOURS = 24

class LightSchedule(object):
    """Class to hold lighting schedule"""

    def __init__(self):
        print("")

    def get_data(self):
        """gets a current copy of the schedule"""
        with open(fileloc) as data_file:
            data = json.load(data_file)

        return data

    def get_percent(self, channel, hour):
        """gets percentage value from schedule"""
        data = self.get_data()
        r = 0
        for x in data['channels']:
            if (x['id'] == channel):
                for y in x['schedule']:
                    if (y['hour'] == hour):
                        r = int(y['percent'])

        if r == None:
            # why you no print?
            # i guess r := None just leaves it at 0
            print("Something is wrong Asked for channel={0} hour={1} giving 0")
            return 0
        else:
            return min(100, max(r, 0))
        return

    def get_pwm(self, channel, hour):
        """gets the pwm value of a channel at a certain hour"""
        return int(round((self.get_percent(channel, hour) / 100) * 4095))

    def get_number_of_channels(self):
        """gets total number of active channels"""
        data = self.get_data()
        c = 0
        for x in data['channels']:
            c += 1
        return c
