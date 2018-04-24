#!/usr/bin/env python3
import logging
import threading
import time
import os
import Server
import websocket

import LightSchedule
import PCA9685
import PCA9685_dummy
import Settings
import Channel
from WeatherType import WeatherType
import json
from objdict import ObjDict

#plugins
#import plugins.watts.watts

DEBUG = True
MAIN_LOOP_TIME = 5
MAIN_LOOP_HEALTH_FREQ = 120

LED_MAX = 4095  # Max Brightness
LED_MIN = 0     # Min Brightness (off)


def makeLogger():
    '''sets up the logger'''
    logging.raiseExceptions = True

    logdir = 'logs/'
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')

    handler = logging.handlers.TimedRotatingFileHandler(logdir + "whet.log",
                                                        when='midnight',
                                                        interval=1,
                                                        backupCount=7)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    debug_handler = logging.handlers.TimedRotatingFileHandler(logdir + "whet-DEBUG.log",
                                                              when='midnight',
                                                              interval=1,
                                                              backupCount=2)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    return logger


def main_loop():
    logger = makeLogger()
    logger.info("Whet started")

    # counts for debug/ health report
    loops = 0
    event_time = 0
    dead_tornado_cnt = 0
    dead_channel_cnt = 0

    # Settings ----------------------------------------------------------------
    settings = Settings.Settings()

    # Server ------------------------------------------------------------------
    tornado_server = Server.Server()
    tornado_server.start()
    time.sleep(1)
    # connect to the server
    

    light_schedule = LightSchedule.LightSchedule()

    # Initialise the PCA9685, if cant use a dummy (for testing on machine that is not pi)
    try:
        pwm = PCA9685.PCA9685()
        # Alternatively specify a different address and/or bus:
        #pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
    except ImportError:
        msg = "UNABLE TO LOAD PCA9685... no pwm values will set!"
        logger.exception(msg)
        print(msg)
        pwm = PCA9685_dummy.PCA9685()

    # Set frequency to 1000hz... LEDS.
    pwm.set_pwm_freq(1000)
    pwm.set_all(LED_MIN)
    time.sleep(1)

    try:
        channel_threads = []

        while True:
            settings.read_file()
            

            # untested
            if not tornado_server.is_alive():
                dead_tornado_cnt += 1
                logger.error("Tornado thread died %s", dead_tornado_cnt)
                tornado_server = Server.Server()
                tornado_server.start()
                time.sleep(1)

            # restart threads if they die, this should never happen
            for i, val in enumerate(channel_threads):
                if not val.is_alive():
                    dead_channel_cnt += 1
                    logger.error(
                        "THREAD %s IS DEAD: Dead thread count = %s", val.c_id, dead_channel_cnt)
                    channel_threads[i] = Channel.Channel(
                        val.c_id, pwm, light_schedule)
                    channel_threads[i].start()

            if len(channel_threads) != light_schedule.get_number_of_channels():
                logger.info("Thread to channel mismatch config=%s threads=%s",
                            light_schedule.get_number_of_channels(), len(channel_threads))
                for i, val in enumerate(channel_threads):
                    channel_threads[i].cancel()
                    while channel_threads[i].is_alive():
                        logger.info("waiting for thread to die")
                        time.sleep(1)
                channel_threads = []  # reset list
                for i in range(light_schedule.get_number_of_channels()):
                    channel_obj = Channel.Channel(i, pwm, light_schedule)
                    channel_threads.append(channel_obj)
                    channel_obj.start()


            
            a_data = []
            conn = websocket.create_connection("ws://localhost:7999/chat/websocket?id=py", timeout=2)
            for i, val in enumerate(channel_threads):
                if val.is_alive:
                    a_data.append(val.broadcast())
            c_data = ObjDict()
            c_data.status = a_data
            conn.send(json.dumps(c_data, sort_keys=True, indent=4))
            conn.close(reason="whet.py loop finished", timeout=2)



            if loops >= MAIN_LOOP_HEALTH_FREQ:
                loops = 0
                logger.info("Dead Channels:%s | Dead Tornados:%s",
                            dead_channel_cnt, dead_tornado_cnt)

            loops += 1

            #revert to normal after set time
            EVENT_TIMEOUT = 3600    #30 minutes = 1800
            if not settings.runmode == 'normal':
                if event_time == 0:
                    logger.info("{} started".format(settings.runmode))
                    event_time = time.time()
                if time.time() - event_time > EVENT_TIMEOUT:
                    logger.info("{} Event has timed out".format(settings.runmode))
                    settings.runmode ='normal'
                    settings.dump_file()
                    event_time = 0
            else:
                event_time = 0



            time.sleep(MAIN_LOOP_TIME)
                

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt Quit')
        pwm.set_all(LED_MIN)
    finally:
        for i, val in enumerate(channel_threads):
            logger.info('Cancel channel %s', i)
            channel_threads[i].cancel()
        pwm.set_all(LED_MIN)

        logger.info('Killing server thread')
        conn.close()
        tornado_server.stop()
        pwm.set_all(LED_MIN)


if __name__ == "__main__":
    main_loop()
