import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class SoundSensor:
    def __init__(self, i2c, channel=ADS.P0):
        self.ads = ADS.ADS1115(i2c)
        self.chan = AnalogIn(self.ads, channel)
        # Calibration constants (SEN0232 datasheet)
        self.V_MIN, self.V_MAX = 0.6, 2.6
        self.DB_MIN, self.DB_MAX = 30, 130

    def voltage_to_db(self, voltage):
        if voltage < self.V_MIN:
            voltage = self.V_MIN
        if voltage > self.V_MAX:
            voltage = self.V_MAX
        return self.DB_MIN + (voltage - self.V_MIN) * (self.DB_MAX - self.DB_MIN) / (self.V_MAX - self.V_MIN)

    def read(self):
        voltage = self.chan.voltage
        return {
            "raw": self.chan.value,
            "voltage": voltage,
            "dB": self.voltage_to_db(voltage)
        }
