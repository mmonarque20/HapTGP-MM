#Code exemple pour tester le fonctionnement du ds3231 (Affichage de la date et heure dans le terminal)

import adafruit_ds3231
import time

import board

def init_horloge():
    i2c = board.I2C() #board.SCL, board.SDA
    rtc = adafruit_ds3231.DS3231(i2c)
    rtc.datetime = time.localtime()
    return rtc

def get_date(rtc):
    while True:
        t = rtc.datetime
        return(f"{t.tm_mday}/{t.tm_mon}/{t.tm_year}")
       
def get_heure(rtc):
    while True:
        t = rtc.datetime
        return(f"{t.tm_hour}:{t.tm_min}:{t.tm_sec}")
        


if __name__ == "__main__":
    rtc = init_horloge()
    print(get_date(rtc))
    try:
        while True:
            print(get_heure(rtc))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt du test horloge.")