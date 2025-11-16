""" Librairie et Code exemple pour tester  le fonctionnement du Bme280 et 
l'utiliser dans d'autres programmes"""

import board
import time
from adafruit_bme280 import basic as adafruit_bme280

# Create sensor object, using the board's default I2C bus.
i2c = board.I2C()   # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)


bme280.sea_level_pressure = 1013.25

def getTemperature():
    return bme280.temperature

def getHumidity():
    return bme280.relative_humidity

def getPressure():
    return bme280.pressure

def getAltitude():
    return bme280.altitude


if __name__ == "__main__":
    while True:
        print("\nTemperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.relative_humidity)
        print("Pressure: %0.1f hPa" % bme280.pressure)
        print("Altitude = %0.2f meters" % bme280.altitude)
        time.sleep(2)
