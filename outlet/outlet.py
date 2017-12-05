#!/usr/bin/env python3

#from pytuya import pytuya
import time
import json
import datetime
import numpy


switch_status = [ False, False, False, False, False]

while True:
    t_info = json.load(open('switch_schedule.json', mode='r'))

    now = datetime.datetime.now()
    midnight = datetime.datetime.combine(now.date(), datetime.time())
    seconds = (now - midnight).seconds


    for switch in t_info['switches']:

        for event in switch['schedule']:
            if (seconds > event['start'] and seconds < event['end']):
                if (not switch_status[switch['id']]):
                    print("Start switch")
            else:
                if (switch_status[switch['id']]):
                    print('Stop Switch')

    time.sleep(5)


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