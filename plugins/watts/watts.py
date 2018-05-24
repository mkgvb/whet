import pywemo
import json
import datetime
import time
import websocket
import os, sys
from whet.DataBase import DataBase


class WattMeter():
        

    def __init__(self):

        self.db = DataBase('power')
        devices = pywemo.discover_devices()
        print(devices)

        if len(devices) == 0:
            devices = [1]
            print('Discovery failed')
            address = '192.168.2.70'
            port = port = pywemo.ouimeaux_device.probe_wemo(address)
            url = 'http://%s:%i/setup.xml' % (address, port)
            devices[0] = pywemo.discovery.device_from_description(url, None)

        self.device = devices[0]

    @property
    def current_draw_watts(self):
        self.device.update_insight_params()
        self.db.writeNow('{:.3f}'.format(round(self.device.current_power / 1000, 3)))
        return '{:.3f}'.format(round(self.device.current_power / 1000, 3))


if False:
    wm = WattMeter()

    while True:
        now = datetime.datetime.now()
        curr = wm.current_draw_watts
        print('{:%H:%M:%S}: {}w'.format(now, curr))

        if now.minute == 0 or now.minute == 30:
            with open('{:%m-%d-%Y}.log'.format(now), 'a+') as f:
                f.write('{:%H:%M:%S}: {}w\n'.format(now, curr))
            time.sleep(120)

        time.sleep(30)

if __name__ == '__main__':
    wm = WattMeter()

    while True:
        time.sleep(10)
        now = datetime.datetime.now()
        watts = wm.current_draw_watts
        print('{:%H:%M:%S}: {}w'.format(now, watts))

        try:
            conn = websocket.create_connection("ws://localhost:7999/chat/websocket?id=outlet")
            msg = {}
            msg['watts'] = watts
            conn.send(json.dumps(msg) )
            conn.close(reason="watts finished", timeout=2)
        except ConnectionRefusedError as e:
            logging.exception("Cant connect to websocket server")


