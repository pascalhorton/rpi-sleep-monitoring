import math
import sys
import time
import datetime
from grove.adc import ADC
from grove.button import Button
from grove.factory import Factory
from grove.gpio import GPIO

slot_loudness_sensor = 0
slot_proximity_sensor = 4
slot_light_sensor = 2
slot_button = 22
slot_led = 24

use_loudness_sensor = True
use_proximity_sensor = True
use_light_sensor = True
use_button = True

debug = True

class GroveLoudnessSensor:

    def __init__(self, channel):
        self.__channel = channel
        self.__adc = ADC()
        self.__sum = 0
        self.__count = 0
        self.__max = 0

    @property
    def value(self):
        return self.__adc.read(self.__channel)

    @property
    def max(self):
        return self.__max

    @property
    def mean(self):
        return self.__sum / max(self.__count, 1)

    def record_value(self):
        self.__sum += self.value
        self.__count += 1
        self.__max = max(self.__max, self.value)

    def reset_records(self):
        self.__sum = 0
        self.__count = 0
        self.__max = 0


class GroveButton(object):
    def __init__(self, pin):
        # High = pressed
        self.__btn = Factory.getButton("GPIO-HIGH", pin)
        self.__last_time = time.time()
        self.__pressed = 0
        self.__btn.on_event(self, GroveButton.__handle_event)

    @property
    def pressed(self):
        return self.__pressed

    def reset_pressed(self):
        self.__pressed = 0

    def __on_press(self):
        self.__pressed = 1

    def __handle_event(self, evt):
        dt, self.__last_time = evt["time"] - self.__last_time, evt["time"]
        if evt["code"] == Button.EV_LEVEL_CHANGED:
            if evt["pressed"]:
                self.__on_press()


class GroveInfraredProximitySensor(GPIO):
    def __init__(self, pin):
        super(GroveInfraredProximitySensor, self).__init__(pin, GPIO.IN)
        self.__counter = 0

    @property
    def counter(self):
        return self.__counter

    def on_detect(self):
        if self.on_event is None:
            self.on_event = self.__handle_event
        self.__counter += 1

    def reset_counter(self):
        self.__counter = 0

    def __handle_event(self, pin, value):
        if value:
            self.on_detect()


class GroveLed(GPIO):
    def __init__(self, pin):
        super(GroveLed, self).__init__(pin, GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(0)

    def long_flash(self):
        self.on()
        time.sleep(3)
        self.off()

    def double_flash(self):
        self.on()
        time.sleep(.2)
        self.off()
        time.sleep(.2)
        self.on()
        time.sleep(.2)
        self.off()


class GroveLightSensor:

    def __init__(self, channel):
        self.__channel = channel
        self.__adc = ADC()
        self.__sum = 0
        self.__count = 0
        self.__max = 0

    @property
    def light(self):
        value = self.__adc.read(self.__channel)
        return value

    @property
    def max(self):
        return self.__max

    @property
    def mean(self):
        return self.__sum / max(self.__count, 1)

    def record_value(self):
        self.__sum += self.light
        self.__count += 1
        self.__max = max(self.__max, self.light)

    def reset_records(self):
        self.__sum = 0
        self.__count = 0
        self.__max = 0


def main():
    f = create_file()

    loudness_sensor = GroveLoudnessSensor(slot_loudness_sensor)
    proximity_sensor = GroveInfraredProximitySensor(slot_proximity_sensor)
    light_sensor = GroveLightSensor(slot_light_sensor)
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

            end = time.time()
            if end - start >= 60:
                f.write(datetime.datetime.now().isoformat())
                if use_loudness_sensor:
                    f.write('{}, {}, '.format(loudness_sensor.mean, loudness_sensor.max))
                    loudness_sensor.reset_records()
                if use_proximity_sensor:
                    f.write('{}, '.format(proximity_sensor.counter))
                    proximity_sensor.reset_counter()
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
                time.sleep(.5)


def create_file():
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H%M_monitoring.csv")
    f = open(filename, 'w')
    f.write('time, ')
    if use_loudness_sensor:
        f.write('loudness_mean, loudness_max, ')
    if use_proximity_sensor:
        f.write('proximity, ')
    if use_button:
        f.write('button, ')
    if use_light_sensor:
        f.write('light_mean, light_max, ')
    f.write('\n'.format())
    return f


if __name__ == '__main__':
    main()
