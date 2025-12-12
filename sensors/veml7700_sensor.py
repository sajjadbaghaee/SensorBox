import adafruit_veml7700

class VEML7700Sensor:
    def __init__(self, i2c):
        self.sensor = adafruit_veml7700.VEML7700(i2c)

    def read(self):
        return {
            "lux": self.sensor.lux
        }
