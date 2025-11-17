import RPi.GPIO as GPIO  # pyright: ignore[reportMissingModuleSource]
import time

# ─── Configuration ─────────────────────────────────────────────────────────────

BUZZER_PIN = 12  # GPIO12 = pin physique 32

# ─── Fonctions ─────────────────────────────────────────────────────────────────

def init_buzzer(pin=BUZZER_PIN):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 440)  # Fréquence par défaut
    return pwm

def bip(pwm, freq, duration=0.5, duty_cycle=50):
    pwm.ChangeFrequency(freq)
    pwm.start(duty_cycle)
    time.sleep(duration)
    pwm.stop()

def test_buzzer(pwm):
    try:
        while True:
            bip(pwm, freq=500)   # Bip grave
            time.sleep(2)
            bip(pwm, freq=1000)  # Bip aigu
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nArrêt du programme.")
    finally:
        pwm.stop()
        GPIO.cleanup()
        print("GPIO nettoyé.")

# ─── Exécution ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pwm = init_buzzer()
    test_buzzer(pwm)