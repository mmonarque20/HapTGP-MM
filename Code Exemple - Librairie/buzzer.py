import RPi.GPIO as GPIO  # pyright: ignore[reportMissingModuleSource]
import time
import math

# ─── Configuration ─────────────────────────────────────────────────────────────

BUZZER_PIN = 12  # GPIO12 = pin physique 32

TRANSPOSITION = 0 
# ─── Fonctions ─────────────────────────────────────────────────────────────────

def init_buzzer(pin=BUZZER_PIN):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 440)  # Fréquence par défaut
    return pwm

def midi_vers_hertz(note_midi):
    """ Convertit un numéro de note MIDI en fréquence (Hz).
        Formule : f = 440 * 2^((d - 69) / 12)"""  
    note_ajustee = note_midi + TRANSPOSITION
    freq = 440.0 * (2.0 ** ((note_ajustee - 69.0) / 12.0))
    return freq  

def bip(pwm, freq, duration=0.5, duty_cycle=50):
    pwm.ChangeFrequency(freq)
    pwm.start(duty_cycle)
    time.sleep(duration)
    pwm.stop()

# --- Séquences musicale ---
def jouer_intro(pwm):
    """
    Joue uniquement les 7 notes de l'intro de Mario Bros.
    """
    # Séquence : (Note MIDI, Durée de son, Durée pause)
    # E5=76, C5=72, G5=79, G4=67
    sequence = [
        (76, 0.10, 0.05),  # Ta
        (76, 0.10, 0.10),  # Ta
        (76, 0.10, 0.10),  # Ta
        (72, 0.10, 0.05),  # Ta
        (76, 0.10, 0.15),  # Ta
        (79, 0.20, 0.20),  # TAAAA (Aigu)
        (67, 0.20, 0.00), # Taaa  (Grave)
    ]

    for note_midi, duree_son, duree_pause in sequence:
        freq = midi_vers_hertz(note_midi)
        
        pwm.ChangeFrequency(freq)
        pwm.start(10)        # Volume/Duty 50%
        time.sleep(duree_son)
        
        pwm.stop()
        time.sleep(duree_pause)



def jouer_musique(pwm):
    """
    Joue une petite séquence musicale de 0.5 sec au total.
    """
    # Définition des notes (fréquence en Hz, durée en secondes)
    sequence = [
        (880, 0.1),   # A5
        (988, 0.1),   # B5
        (1047, 0.1),  # C6
        (1319, 0.1),  # E6
        (1047, 0.1),  # C6
    ]

    for freq, duree in sequence:
        pwm.ChangeFrequency(freq)        # règle la fréquence
        pwm.start(10)
        time.sleep(duree)
        pwm.stop()     # coupe le son entre les notes


# --- Fonction de test --- 
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