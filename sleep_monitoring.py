import time
import sys
import os
import datetime
from pathlib import Path
from sensors import *


# Define sensor slots
slot_loudness_sensor = 6
slot_proximity_sensor = 5
slot_motion_sensor = 23
slot_light_sensor = 2
slot_temp_humidity_sensor = 22
slot_button = 22
slot_led = 24

# Select sensors to enable
use_loudness_sensor = True
use_proximity_sensor = False
use_motion_sensor = True
use_light_sensor = True
use_temp_humidity_sensor = True
use_button = True

# Debug mode
debug = False


def main():
    # Check arguments provided
    if len(sys.argv) < 2:
        print('Usage: {} output_path'.format(sys.argv[0]))
        sys.exit(1)

    f = create_file(sys.argv[1])

    loudness_sensor = GroveLoudnessSensor(slot_loudness_sensor)
    proximity_sensor = GroveInfraredProximitySensor(slot_proximity_sensor)
    motion_sensor = PIRMotionSensor(slot_motion_sensor)
    light_sensor = GroveLightSensor(slot_light_sensor)
    temp_humidity_sensor = GroveTemperatureHumiditySensor(slot_temp_humidity_sensor)
    button = GroveButton(slot_button)
    led = GroveLed(slot_led)

    print('Starting monitoring...')
    
    # Flash the LED to signal that the monitoring is starting
    led.long_flash()

    # Monitor continuously
    while True:
        start = time.time()
        counter = 0

        # Loop for measuring and writing data to file
        while True:
            counter += 1
            loudness_sensor.record_value()
            light_sensor.record_value()

            # Measure temperature and humidity every 20 iterations (~seconds)
            if counter % 20 == 0:
                temp_humidity_sensor.record_value()

            if debug:
                print('loudness: {}'.format(loudness_sensor.value))
                print('proximity: {}'.format(proximity_sensor.counter))
                print('motion: {}'.format(motion_sensor.counter))
                print('button: {}'.format(button.pressed))
                print('light: {}'.format(light_sensor.light))
                if counter % 20 == 0:
                    humid, temp = temp_humidity_sensor.temperature_and_humidity
                    print('temperature: {:.1f}'.format(temp))
                    print('humidity: {:.1f}'.format(humid))

            end = time.time()
            
            # Write the measured values to the file every minute and reset sensors
            if end - start >= 60:
                dt = datetime.datetime.now()
                dt = dt.replace(microsecond=0)
                f.write('{}, '.format(dt.isoformat()))
                if use_loudness_sensor:
                    f.write('{:.1f}, {}, '.format(loudness_sensor.mean, loudness_sensor.max))
                    loudness_sensor.reset_records()
                if use_proximity_sensor:
                    f.write('{}, '.format(proximity_sensor.counter))
                    proximity_sensor.reset_counter()
                if use_motion_sensor:
                    f.write('{}, '.format(motion_sensor.counter))
                    motion_sensor.reset_counter()
                if use_temp_humidity_sensor:
                    f.write('{:.1f}, {:.1f}, '.format(temp_humidity_sensor.temperature, temp_humidity_sensor.humidity))
                    temp_humidity_sensor.reset_records()
                if use_light_sensor:
                    f.write('{:.1f}, {}, '.format(light_sensor.mean, light_sensor.max))
                    light_sensor.reset_records()
                if use_button:
                    f.write('{}, '.format(button.pressed))
                    button.reset_pressed()
                f.write('\n'.format())
                led.flash()
                break
            else:
                # Sleep 1 sec
                time.sleep(1)


def create_file(dir_path):
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H%M_monitoring.csv")
    f = open(os.path.join(dir_path, filename), 'w', buffering=1)
    f.write('time, ')
    if use_loudness_sensor:
        f.write('loudness_mean, loudness_max, ')
    if use_proximity_sensor:
        f.write('proximity, ')
    if use_motion_sensor:
        f.write('motion, ')
    if use_temp_humidity_sensor:
        f.write('temperature, humidity, ')
    if use_light_sensor:
        f.write('light_mean, light_max, ')
    if use_button:
        f.write('button, ')
    f.write('\n'.format())
    return f


if __name__ == '__main__':
    main()
