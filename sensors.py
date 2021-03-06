import time
from grove.adc import ADC
from grove.button import Button
from grove.factory import Factory
from grove.gpio import GPIO
import seeed_dht


class GroveTemperatureHumiditySensor:

    def __init__(self, channel):
        self.__sensor = seeed_dht.DHT("22", 12)
        self.__humidity_sum = 0
        self.__humidity_count = 0
        self.__temperature_sum = 0
        self.__temperature_count = 0

    @property
    def humidity(self):
        humidity, temp = self.__sensor.read()
        return humidity

    @property
    def temperature(self):
        humidity, temp = self.__sensor.read()
        return temp

    @property
    def temperature_and_humidity(self):
        return self.__sensor.read()

    def record_value(self):
        humidity, temp = self.__sensor.read()
        self.__humidity_sum += humidity
        self.__humidity_count += 1
        self.__temperature_sum += temp
        self.__temperature_count += 1

    def reset_records(self):
        self.__humidity_sum = 0
        self.__humidity_count = 0
        self.__temperature_sum = 0
        self.__temperature_count = 0


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


class PIRMotionSensor(GPIO):
    def __init__(self, pin):
        super(PIRMotionSensor, self).__init__(pin, GPIO.IN)
        self.__counter = 0
        self._on_detect = self.increment_counter
        self.on_event = self._handle_event

    @property
    def counter(self):
        return self.__counter

    def reset_counter(self):
        self.__counter = 0

    def increment_counter(self):
        self.__counter += 1
        print('-- Motion detected --')

    @property
    def on_detect(self):
        return self._on_detect

    def _handle_event(self, pin, value):
        if value:
            if callable(self._on_detect):
                self._on_detect()


class GroveInfraredProximitySensor(GPIO):
    def __init__(self, pin):
        super(GroveInfraredProximitySensor, self).__init__(pin, GPIO.IN)
        self.__counter = 0
        self._on_detect = self.increment_counter
        self.on_event = self._handle_event

    @property
    def counter(self):
        return self.__counter

    def reset_counter(self):
        self.__counter = 0

    def increment_counter(self):
        self.__counter += 1
        print('-- Proximity detected --')

    @property
    def on_detect(self):
        return self._on_detect

    def _handle_event(self, pin, value):
        if value:
            if callable(self._on_detect):
                self._on_detect()


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

    def flash(self):
        self.on()
        time.sleep(.1)
        self.off()

    def double_flash(self):
        self.on()
        time.sleep(.1)
        self.off()
        time.sleep(.1)
        self.on()
        time.sleep(.1)
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
