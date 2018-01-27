#!/usr/bin/env python3

from python_tuya import pytuya
import time
import json
import datetime
import logging.handlers
from pushbullet import PushBullet
from pprint import pprint


with open('env.json') as env_file:
    env = json.load(env_file)

LOG_FILE_NAME = 'log/outlet.log'
LOGGING_LEVEL = logging.INFO

formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME, mode='a', maxBytes=5000000, backupCount=5)
handler.setFormatter(formatter)
log = logging.getLogger("outlet")
log.addHandler(handler)
log.setLevel(LOGGING_LEVEL)

if 'pb_api_key' in env:
    pb = PushBullet(env['pb_api_key'])
else:
    log.info("No pushbullet api key found, pb_api_key")

def toTime(strTime):
    thetime = time.strptime(strTime, "%H:%M")
    return thetime



connErrorCount = 0
d = pytuya.OutletDevice(env['dev_id'], env['address'], env['local_key'])
switch_status = {}


while True:
    t_info = json.load(open('outlet_schedule.json', mode='r'))
    looptime = env['looptime']
    

    sysTime = time.strptime(datetime.datetime.now().strftime('%H:%M'), "%H:%M")

    try:
        switch_status = d.status()['dps']

        log.info('ConnErrors: '+ str(connErrorCount) 
            + '|' + "time: " + time.strftime("%H:%M:%S",sysTime)
            + '|' + 'Switch Statuses: %r' % switch_status)

        for outlet in t_info['outlet_schedule']:
            active_event = False
            for event in outlet['schedule']:
                if (sysTime > toTime(event['start']) and sysTime < toTime(event['end'])):
                    active_event = True
                    if (not switch_status[str(outlet['id'])]):
                        log.info('Turning on... ' + outlet['name'])
                        d.set_status(True, outlet['id'])
                        time.sleep(looptime/2)

            if not active_event:
                if (switch_status[str(outlet['id'])]):
                    log.info('Turning off..' +outlet['name'])
                    d.set_status(False, outlet['id'])
                    time.sleep(looptime/2)
    except ConnectionResetError:
        print("Connection Error")
        connErrorCount += 1
        pb.push_note('outlet.py error', 'count = '+ str(connErrorCount) + ' | ' + str(sorted(switch_status))  )
    

    time.sleep(looptime)


