""" Librairie et Code exemple pour calibrer et tester  le fonctionnement du Veml7700 et 
l'utiliser dans d'autres programmes"""

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_veml7700
import numpy as np

veml_lux = [0, 4295, 6980, 9370, 11600, 13693, 15635, 17576, 18883, 20372, 21486, 22751, 23961, 26411, 27879, 29707, 30618, 30693, 32070, 33037, 33923]
real_lux = [0, 1722, 2850, 3980, 5100, 6210, 7320, 8530, 9360, 10360, 11140, 12080, 13000, 14960, 16160, 17850, 18740, 18830, 2100, 21200, 22100]

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
veml7700 = adafruit_veml7700.VEML7700(i2c, address=0x10)
time.sleep(0.5) # laisser le capteur s'initialiser

def getLuminosite():
    raw = veml7700.light
    calibrated = np.interp(raw, veml_lux, real_lux)
    return calibrated
    

if __name__ == "__main__":
    while True:
        print(f"Ambient light: {getLuminosite():.1f} lux")
        time.sleep(2)