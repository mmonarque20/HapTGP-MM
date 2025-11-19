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
        print(f"Température : {getTemperature():.1f} °C")
        print(f"Humidité : {getHumidity():.1f} %")
        print(f"Pression : {getPressure():.1f} hpa")
        print(f"Altitude : {getAltitude():.1f} mètres" )
        time.sleep(2)
