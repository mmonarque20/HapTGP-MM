"""Programme de feedback du moteur et du buzzer selon certains angles"""

from smbus2 import SMBus
import time
import magneto           # Librairie Magnétomètre (magneto.py)
import moteurHaptique    # Librairie Moteur (moteurHaptique.py)
import buzzer            # Librairie du Buzzer   (buzzer.py)


# --- Constantes Globales ---
BUS_MOTEUR = 1
BUS_MAGNETO = 1
BUZZER_PIN = 12 
EFFET_FORT_CLICK = 0x4B # Effet moteur
SEUIL_ANGLE = 5         # Marge autour des angles cibles 

"""Programme init_feedback_modules: Initialise les modules de feedback : Buzzer, Magnétomètre et moteur haptique"""
def init_feedback_modules():
    # --- Initialisation du Buzzer ---
    pwm = buzzer.init_buzzer() 
    
    # --- Initialisation du Moteur Haptique ---
    try:
        with SMBus(BUS_MOTEUR) as bus_moteur:
            moteurHaptique.init_moteur(bus_moteur)
            moteurHaptique.definir_effet(bus_moteur, EFFET_FORT_CLICK)

            # Test de l'effet à l'initialisation
            moteurHaptique.jouer_effet(bus_moteur)
            print("Effet moteur testé.")
            
    except Exception as e:
        print(f"Erreur lors de l'initialisation du moteur : {e}")
        return # Arrête le programme si le moteur ne s'initialise pas
   
    # --- Initialisation du magnétomètre ---
    try:
        with SMBus(BUS_MAGNETO) as bus_magneto:
            magneto.initMagneto(bus_magneto)   
            print("Magnétomètre initialisé.")
    except Exception as e:
        print(f"Erreur d'initialisation du Magnéto : {e}")
        return # arrête le programme si le magnéto ne s'initialise pas
    
    return pwm, BUS_MAGNETO


""" Programme is_angle_target: Vérifie si l'angle est proche de 0, 72, 144, 216 ou 288 degrés."""
def is_angle_target(angle, cibles=None, seuil=SEUIL_ANGLE):
    normalized_angle = angle % 360 # Assure que l'angle est entre 0 et 360

    # Angles cibles
    if cibles is None:
        cibles = [0, 72, 144, 216, 288]
    for cible in cibles:
        if abs(normalized_angle - cible) <= seuil:
            return True
        if cible == 0 and normalized_angle >= 360 - seuil:
            return True
    return False


# --- FeedBack ---
""" Programme run_feedback_system: Boucle principale du programme"""


def jouer_haptique(bus):
    effet_long= 0x0C
    moteurHaptique.jouer_sequence(bus,effet_id=effet_long, repetitions=4, duree_par_effet=0.3)   

def feedback(current_angle, pwm, haptic_triggered, bus):
    if is_angle_target(current_angle):
        
        if not haptic_triggered:
            buzzer.jouer_musique(pwm)
            jouer_haptique(bus)
            print(f"*** VIBRATION À {current_angle:.1f}° ***")
            haptic_triggered = True
    else:
        haptic_triggered = False
    return haptic_triggered


# --- Lecture d'angle ---
def lire_angle(bus_magneto):
    angle_brut, angle_corrige, angle_filtre = magneto.getAngle(bus_magneto)
    return angle_corrige

# --- Boucle du système --- 
def run_feedback_system(pwm, bus_magneto):
    haptic_triggered = False 
    try:
        with SMBus(BUS_MAGNETO) as bus_magneto:
            while True:
                current_angle = lire_angle(bus_magneto) # On utilise l'angle corrigé
                haptic_triggered = feedback(current_angle, pwm, haptic_triggered)
                print(f"Angle : {current_angle:.1f}°")
                time.sleep(0.05)
    except Exception as e:
        print(f"Erreur lors de la lecture du magnétomètre : {e}")


if __name__ == "__main__":
    pwm, bus_magneto = init_feedback_modules()
    if pwm and bus_magneto: # si pwm et bus_magneto existent
        run_feedback_system(pwm, bus_magneto)