import math
import sys
import time
import datetime
from grove.adc import ADC

pin_loudness_sensor = 0
pin_button = 2
use_loudness_sensor = True


class GroveLoudnessSensor:

    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def value(self):
        return self.adc.read(self.channel)


Grove = GroveLoudnessSensor


def main():
    f = create_file()

    loudness_sensor = GroveLoudnessSensor(pin_loudness_sensor)

    print('Starting monitoring...')
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
            print(end - start)
            if end - start >= 60:
                f.write(datetime.datetime.now().isoformat())
                if use_loudness_sensor:
                    f.write('{}, {}, '.format(loudness_sum/loudness_count, loudness_max))
                f.write('\n'.format())
                break
            else:
                time.sleep(.5)


def create_file():
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M")
    f = open(filename, 'w')
    f.write('time, ')
    if use_loudness_sensor:
        f.write('loudness_mean, loudness_max, ')
    f.write('\n'.format())
    return f


if __name__ == '__main__':
    main()
