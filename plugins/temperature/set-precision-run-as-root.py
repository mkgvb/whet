from w1thermsensor import W1ThermSensor #https://github.com/timofurrer/w1thermsensor#usage-as-python-package

# ADDED TO BOTTOM OF /boot/config/.txt
# dtoverlay=w1-gpio


### examples
# sensor = W1ThermSensor()
#sensor.set_precision(9)

# temperature_in_celsius = sensor.get_temperature()
# temperature_in_all_units = sensor.get_temperatures([
#     W1ThermSensor.DEGREES_C,
#     W1ThermSensor.DEGREES_F,
#     W1ThermSensor.KELVIN])


#set to lowest resolution precision -- should be faster?
# this needs to be set after every power cycle
#needs root
set_as = 9
for s in W1ThermSensor.get_available_sensors():
  s.set_precision(set_as)
  print('set {} to {}'.format(s.id, set_as) )
