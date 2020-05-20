import math
import sys
import time
import datetime
from grove.adc import ADC
from grove.button import Button
from grove.factory import Factory
from grove.gpio import GPIO

slot_loudness_sensor = 0
slot_proximity_sensor = 2
slot_button = 22
slot_led = 24
use_loudness_sensor = True
use_proximity_sensor = True
use_button = True


class GroveLoudnessSensor:

    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def value(self):
        return self.adc.read(self.channel)


class GroveButton(object):
    def __init__(self, pin):
        # High = pressed
        self.__btn = Factory.getButton("GPIO-HIGH", pin)
        self.__last_time = time.time()
        self.__pressed = False
        self.__btn.on_event(self, GroveButton.__handle_event)

    @property
    def pressed(self):
        return self.__pressed

    def reset_pressed(self):
        self.__pressed = False

    def __on_press(self):
        self.__pressed = True

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


def main():
    f = create_file()

    loudness_sensor = GroveLoudnessSensor(slot_loudness_sensor)
    proximity_sensor = GroveInfraredProximitySensor(slot_proximity_sensor)
    button = GroveButton(slot_button)
    led = GroveLed(slot_led)

    print('Starting monitoring...')
    led.on()
    time.sleep(3)
    led.off()

    while True:
        start = time.time()
        loudness_max = 0
        loudness_sum = 0
        loudness_count = 0

        while True:
            loudness_value = loudness_sensor.value
            if loudness_value > 10:
                loudness_max = max(loudness_max, loudness_value)
                loudness_sum += loudness_value
                loudness_count += 1

            end = time.time()
            if end - start >= 60:
                f.write(datetime.datetime.now().isoformat())
                if use_loudness_sensor:
                    f.write('{}, {}, '.format(loudness_sum/loudness_count, loudness_max))
                if use_proximity_sensor:
                    f.write('{}, '.format(proximity_sensor.counter))
                    proximity_sensor.reset_counter()
                if use_button:
                    f.write('{}, '.format(button.pressed))
                    button.reset_pressed()
                f.write('\n'.format())
                led.on()
                time.sleep(.2)
                led.off()
                led.on()
                time.sleep(.2)
                led.off()
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
    f.write('\n'.format())
    return f


if __name__ == '__main__':
    main()
