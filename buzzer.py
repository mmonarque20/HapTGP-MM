#Code exemple pour tester le fonctionnement du Buzzer

import RPi.GPIO as GPIO # pyright: ignore[reportMissingModuleSource]
import time

BuzzerPin = 12  # D12 = GPIO12 = pin physique 32

# Initialisation GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BuzzerPin, GPIO.OUT)

# Initialisation PWM sur le buzzer (valeur par défaut, sera modifiée dans la boucle)
pwm = GPIO.PWM(BuzzerPin, 440)

try:
    while True:
        # Premier bip
        pwm.ChangeFrequency(500)  # son à 500 Hz
        pwm.start(50)
        time.sleep(0.5)
        pwm.stop()

        time.sleep(2)  # pause de 2 secondes

        # Deuxième bip
        pwm.ChangeFrequency(1000)  # son plus aigu
        pwm.start(50)
        time.sleep(0.5)
        pwm.stop()

        time.sleep(2)

except KeyboardInterrupt:
    print("\nArrêt du programme.")
finally:
    pwm.stop()
    GPIO.cleanup()
