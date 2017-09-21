import json
import math
import WeatherType
import pickle

fileloc = 'json/settings.json'


class Settings2(object):
    """Class to hold settings"""
    dictionary = dict(
        weather="normal",
        catchup_on=True,
        catchup_time=5,
        sound_on=True,
        storms_on=False,
        storms_start_time = 21,
        storms_end_time = 0,
        storms_freq = 1,
        clouds_on = True,
        clouds_start_time = 21,
        clouds_end_time = 0,
        clouds_freq = 1)



    def __init__(self):
        

        #print(json.dumps(self.dictionary, ensure_ascii=False))
        self.refresh_data()
        print(" next")
        #print(json.dumps(self.dictionary, ensure_ascii=False))
        print(json.dumps(self.dictionary))

    def refresh_data(self):
        """gets a current copy of the settings"""
        with open(fileloc) as data_file:
            self.dictionary = json.load(data_file)




