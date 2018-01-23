#!/usr/bin/env python3

from python_tuya import pytuya
import time
import json
import datetime
import logging.handlers

LOG_FILE_NAME = 'log/outlet.log'
LOGGING_LEVEL = logging.INFO

formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME, mode='a', maxBytes=5000000, backupCount=5)
handler.setFormatter(formatter)
log = logging.getLogger("outlet")
log.addHandler(handler)
log.setLevel(LOGGING_LEVEL)



connErrorCount = 0
d = pytuya.OutletDevice('012003822c3ae84144d5', '192.168.2.124', 'cb6de23c996a53c1')
switch_status = [ False, False, False, False, False]


while True:
    t_info = json.load(open('switch_schedule.json', mode='r'))
    

    now = datetime.datetime.now()
    midnight = datetime.datetime.combine(now.date(), datetime.time())
    seconds = (now - midnight).seconds
            
    log.info('ConnErrors: '+ str(connErrorCount) + '|' + "time: " + str(seconds) + '|' + 'Switch Statuses: %r' % switch_status )
    #log.info('Switch Statuses: %r' % switch_status)
    #log.info('Connection Errors: '+ str(connErrorCount))
    #print('state (bool, true is ON) %r' % data['dps']['1'])  # Show status of first controlled switch on device

    try:
        switch_status = d.status()['dps']

        for switch in t_info['switches']:
            for event in switch['schedule']:
                if (seconds > event['start'] and seconds < event['end']):
                    d.set_status(True, switch['id'])
                    print(switch['name'] + " - ON")
                else:
                    d.set_status(False, switch['id'])
                    print(switch['name'] + " - OFF")
    except ConnectionResetError:
        print("Connection Error")
        connErrorCount += 1
    



                # pulse_on_ticks = event.get('pulse_on_ticks', None)
                # pulse_off_ticks = event.get('pulse_off_ticks', None)
                # if pulse_on_ticks is not None and pulse_on_ticks is not None:
                #     tick += 1


                

    time.sleep(t_info['looptime'])


# d_info = json.load(open('device.json',mode='r'))
# #d = pytuya.OutletDevice('DEVICE_ID_HERE', 'IP_ADDRESS_HERE', 'LOCAL_KEY_HERE')
# #d = pytuya.OutletDevice('012003822c3ae84144d5', '192.168.2.124', 'cb6de23c996a53c1')
# d = pytuya.OutletDevice(d_info['device_id'], d_info['ip'],d_info['local_key'])
# data = d.status()  # NOTE this does NOT require a valid key
# print('Dictionary %r' % data)
# print('state (bool, true is ON) %r' % data['dps']['3'])  # Show status of first controlled switch on device

# # Toggle switch state
# switch_state = data['dps']['3']
# data = d.set_status(not switch_state, 3)  # This requires a valid key
# if data:
#     print('set_status() result %r' % data)

# # on a switch that has 4 controllable ports, turn the fourth OFF (1 is the first)
# #data = d.set_status(False, 3)
# if data:
#     print('set_status() result %r' % data)
#     print('set_status() extrat %r' % data[20:-8])


# id = 1
# while True:
#     data = d.status()
#     print('state (bool, true is ON) %r' % data['dps'][str(id)])
#     switch_state = data['dps'][str(id)]
#     data = d.set_status(not switch_state, id)  # This requires a valid key
#     time.sleep(5)
#     id += 1
#     if id > 5:
#         id = 1