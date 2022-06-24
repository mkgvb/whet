#!/usr/bin/env python3

import os
import pytuya
import time
import json
import datetime
import socket
import logging.handlers
from pushbullet import PushBullet
from websocket import create_connection


with open('env.json', mode='r') as env_file:
    env = json.load(env_file)

LOG_FILE_NAME = 'log/outlet.log'
LOGGING_LEVEL = logging.INFO

formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME, mode='a', maxBytes=500, backupCount=5)
handler.setFormatter(formatter)
log = logging.getLogger("outlet")
log.addHandler(handler)
log.setLevel(LOGGING_LEVEL)

if 'pb_api_key' in env:
    #pb = PushBullet(env['pb_api_key'])
    log.info("Pushbullet is disabled")
else:
    log.info("No pushbullet api key found, pb_api_key")

def toTime(strTime):
    thetime = time.strptime(strTime, "%H:%M")
    return thetime

print(socket.gethostbyname(env['address']))
address = socket.gethostbyname(env['address'])

d = pytuya.OutletDevice(env['dev_id'], env['address'], env['local_key'])


def run():
    connErrorCount = 0
    t_info = json.load(open('../../json/outlet_schedule.json', mode='r'))
    looptime = env['looptime']
    switch_status = {}
    

    sysTime = time.strptime(datetime.datetime.now().strftime('%H:%M'), "%H:%M")

    try:
        switch_status = d.status()['dps']

        for outlet in t_info['outlet_schedule']:
            outlet['active_event'] = False
            for event in outlet['schedule']:
                if (sysTime > toTime(event['start']) and sysTime < toTime(event['end'])):
                    outlet['active_event'] = True
                    if (not switch_status[str(outlet['id'])]):
                        log.info('Turning on... ' + outlet['name'])
                        if not env['DEBUG']: d.set_status(True, outlet['id'])
                        time.sleep(looptime/2)
                        log.info('Switch Statuses: %r' % switch_status)

            if not outlet['active_event']:
                if (switch_status[str(outlet['id'])]):
                    log.info('Turning off..' +outlet['name'])
                    if not env['DEBUG']: d.set_status(False, outlet['id'])
                    time.sleep(looptime/2)
                    log.info('Switch Statuses: %r' % switch_status)
    except ConnectionResetError:
        logging.exception("Connection Error")
        connErrorCount += 1
        #pb.push_note('outlet.py error', 'count = '+ str(connErrorCount) + ' | ' + str(sorted(switch_status))  )
    
    try:
        conn = create_connection("ws://localhost:7999/chat/websocket?id=outlet")
        conn.send('{ "outlet_status": ' + json.dumps(t_info) + '}' )
        conn.close(reason="outlet.py finished", timeout=2)
    except ConnectionRefusedError as e:
        logging.exception("Cant connect to websocket server")



if __name__ == "__main__":
    while True:
        run()
        time.sleep(5)
        timeout = 0
        while os.path.isfile('/tmp/disable-outlet-schedule.flag') and timeout < 1800:
            print('disabled!')
            time.sleep(1)
            timeout += 1
        if timeout > 1800:
            print('timed out!')
            os.remove('/tmp/disable-outlet-schedule.flag')




