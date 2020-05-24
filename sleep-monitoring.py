import time
import datetime
from sensors import *


slot_loudness_sensor = 6
slot_proximity_sensor = 0
slot_light_sensor = 2
slot_temp_humidity_sensor = 22
slot_button = 22
slot_led = 24

use_loudness_sensor = True
use_proximity_sensor = True
use_light_sensor = True
use_temp_humidity_sensor = True
use_button = True

debug = False


def main():
    f = create_file()

    loudness_sensor = GroveLoudnessSensor(slot_loudness_sensor)
    proximity_sensor = GroveInfraredProximitySensor(slot_proximity_sensor)
    light_sensor = GroveLightSensor(slot_light_sensor)
    temp_humidity_sensor = GroveTemperatureHumiditySensor(slot_temp_humidity_sensor)
    button = GroveButton(slot_button)
    led = GroveLed(slot_led)

    print('Starting monitoring...')
    led.long_flash()

    while True:
        start = time.time()

        while True:
            loudness_sensor.record_value()

            if debug:
                print('loudness: {}'.format(loudness_sensor.value))
                print('proximity: {}'.format(proximity_sensor.counter))
                print('button: {}'.format(button.pressed))
                print('light: {}'.format(light_sensor.light))
                humid, temp = temp_humidity_sensor.temperature_and_humidity
                print('temperature: {}'.format(temp))
                print('humidity: {}'.format(humid))

            end = time.time()
            if end - start >= 60:
                f.write('{}, '.format(datetime.datetime.now().isoformat()))
                if use_loudness_sensor:
                    f.write('{}, {}, '.format(loudness_sensor.mean, loudness_sensor.max))
                    loudness_sensor.reset_records()
                if use_proximity_sensor:
                    f.write('{}, '.format(proximity_sensor.counter))
                    proximity_sensor.reset_counter()
                if use_temp_humidity_sensor:
                    f.write('{}, {}, '.format(temp_humidity_sensor.temperature, temp_humidity_sensor.humidity))
                    temp_humidity_sensor.reset_records()
                if use_button:
                    f.write('{}, '.format(button.pressed))
                    button.reset_pressed()
                if use_light_sensor:
                    f.write('{}, {}, '.format(light_sensor.mean, light_sensor.max))
                    light_sensor.reset_records()
                f.write('\n'.format())
                led.double_flash()
                break
            else:
                time.sleep(1)


def create_file():
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H%M_monitoring.csv")
    f = open(filename, 'w', buffering=1)
    f.write('time, ')
    if use_loudness_sensor:
        f.write('loudness_mean, loudness_max, ')
    if use_proximity_sensor:
        f.write('proximity, ')
    if use_temp_humidity_sensor:
        f.write('temperature, humidity, ')
    if use_button:
        f.write('button, ')
    if use_light_sensor:
        f.write('light_mean, light_max, ')
    f.write('\n'.format())
    return f


if __name__ == '__main__':
    main()
