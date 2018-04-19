import pywemo
import json
import datetime
import time


class WattMeter():

    def __init__(self):

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
        return '{:.3f}'.format(round(self.device.current_power / 1000, 3))


if __name__ == '__main__':
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
