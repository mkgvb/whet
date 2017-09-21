
import json
import math

fileloc = 'json/schedule.json'

#think i only want channel numbers only sent once so thread numbers dont change
num_active_channels = 0

HOURS = 24

class LightSchedule(object):
    """Class to hold lighting schedule"""
    

    def __init__(self):
        data = self.GetData()
        c = 0
        for x in data['channels']:
            c += 1
        num_active_channels = c

    def GetData(self):
        with open(fileloc) as data_file:  
            data = json.load(data_file)

        return data

    def GetPercent(self, channel, hour):
        data = self.GetData()
        r = 0
        for x in data['channels']:
            if (x['id'] == channel):
                for y in x['schedule']:
                    if (y['hour'] == hour):
                        r = int(y['percent'])
        
        if r == None:
            #why you no print?
            # i guess r := None just leaves it at 0
            print("Something is wrong Asked for channel={0} hour={1} giving 0")
            return 0
        else:
            return min(100,max(r,0))
        return 

    def GetPwm(self, channel, hour):
        return int(round((self.GetPercent(channel, hour) / 100) * 4095))

    def GetNumberOfChannels(self):
        data = self.GetData()
        c = 0
        for x in data['channels']:
            c += 1
        return c
    

    