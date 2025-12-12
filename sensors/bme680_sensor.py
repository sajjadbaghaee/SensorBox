import board
import busio
import adafruit_bme680

class BME680Sensor:
    def __init__(self, i2c):
        for addr in (0x76, 0x77):
            try:
                self.sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=addr)
                print(f"BME680 detected at 0x{addr:02X}")
                break
            except Exception:
                self.sensor = None
        if self.sensor is None:
            raise RuntimeError("No BME680 detected on I2C bus")
        
        self.sensor.sea_level_pressure = 1013.25

    def read(self):
        return {
            "temperature": self.sensor.temperature,
            "humidity": self.sensor.humidity,
            "pressure": self.sensor.pressure,
            "gas": self.sensor.gas,
            "altitude": self.sensor.altitude,
        }
