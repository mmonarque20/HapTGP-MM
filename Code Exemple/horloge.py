#Code exemple pour tester le fonctionnement du ds3231

import adafruit_ds3231
import time

import board

i2c = board.I2C() #board.SCL, board.SDA

rtc = adafruit_ds3231.DS3231(i2c)

rtc.datetime = time.localtime()

while True:
    t = rtc.datetime
    print(f"{t.tm_mday}/{t.tm_mon}/{t.tm_year} - {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
    time.sleep(1)

