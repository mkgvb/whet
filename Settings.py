import json
import math
import WeatherType

fileloc = 'json/settings.json'


class Settings(object):
    """Class to hold settings"""
    dictionary = {}
    weather = WeatherType.WeatherType.normal
    catchup_on = True

    def __init__(self):
        
        self.dictionary["weather"] = "normal"
        self.dictionary["catchup_on"] = True
        self.dictionary["catchup_time"] = 5
        self.dictionary["sound_on"] = True
        self.dictionary["storms_on"] = False
        self.dictionary["storms_start_time"] = 21
        self.dictionary["storms_end_time"] = 0
        self.dictionary["storms_freq"] = 1
        self.dictionary["clouds_on"] = True
        self.dictionary["clouds_start_time"] = 21
        self.dictionary["clouds_end_time"] = 0
        self.dictionary["clouds_freq"] = 1 

        print(json.dumps(self.dictionary, ensure_ascii=False))
        self.refresh_data()
        print(" next")
        print(json.dumps(self.dictionary, ensure_ascii=False))

    def refresh_data(self):
        """gets a current copy of the settings"""
        with open(fileloc) as data_file:
            self.dictionary = json.load(data_file)

    def get_data(self):
        """gets a current copy of the settings"""
        with open(fileloc) as data_file:
            data = json.load(data_file)

        return data


