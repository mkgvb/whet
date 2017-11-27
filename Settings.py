'''Holds Settings'''
import logging
import json
from WeatherType import WeatherType
import os


FILELOC = 'json/whet_settings.json'

class Settings(object):
    """Class to hold settings"""
    # pylint: disable=too-many-instance-attributes
    logger = logging.getLogger('__main__')
    last_modified_time = 0  


    def __init__(self):
        try:
            self.read_file()
            self.weather = 'normal' #always start with normal weather
            self.dump_file()
            self.last_modified_time = os.stat(FILELOC).st_mtime
        except IOError:
            self.logger.info("No settings file found...using defaults and creating file ")

            self.weather = "normal"  # todo make this the enum
            self.catchup_on = True
            self.catchup_steps = 255
            self.catchup_time = 5
            self.clouds_random_on = False
            self.clouds_random_start_time = 13
            self.clouds_random_end_time = 15
            self.clouds_random_freq = 20
            self.clouds_dim_percent = .20
            self.clouds_dim_resolution = 255
            self.clouds_dim_speed = .05
            self.storms_random_on = True
            self.storms_random_start_time = 21
            self.storms_random_end_time = 0
            self.storms_random_freq = 1000
            self.sound_on = True

            self.dump_file()
            self.last_modified_time = os.stat(FILELOC).st_mtime

    def dump_file(self):
        '''dumps json representation of obj to disk'''
        with open(FILELOC, 'w') as data_file:
            string = '{"settings":'
            string += json.dumps(
                self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
            string += '}'
            data_file.write(string)

    def read_file(self):
        '''reads file from disk'''
        if self.last_modified_time != os.stat(FILELOC).st_mtime:
            with open(FILELOC) as data_file:
                self.__dict__ = json.load(data_file)["settings"]
