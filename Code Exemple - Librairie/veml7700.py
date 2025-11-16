""" Librairie et Code exemple pour tester  le fonctionnement du Veml7700 et 
l'utiliser dans d'autres programmes"""

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_veml7700

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
veml7700 = adafruit_veml7700.VEML7700(i2c, address=0x10)
time.sleep(0.5) # laisser le capteur s'initialiser

def getLuminosite():
    return veml7700.light
    

if __name__ == "__main__":
    while True:
        print("Ambient light: ", veml7700.light, "lux")
        time.sleep(2)