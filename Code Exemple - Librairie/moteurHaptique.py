# Programme de test de fonctionnement du DRV2605L et librairie pour utilisation dans les autres programmes

import time
import smbus

# Adresse I2C du DRV2605L
DRV_ADDR = 0x5A

# Registres du DRV2605L
REG_MODE = 0x01
REG_GO = 0x0C
REG_SEQ_BASE = 0x04  
REG_OVERDRIVE = 0xFF
REG_LIB_SEL = 0x03

def init_moteur(bus):
    """Initialise le DRV2605L."""
    bus.write_byte_data(DRV_ADDR, REG_MODE, 0x00)       # Mode interne
    bus.write_byte_data(DRV_ADDR, REG_LIB_SEL, 0x01)    # Librairie ERM
    bus.write_byte_data(DRV_ADDR, REG_OVERDRIVE, 0xFF)  # Overdrive max

def definir_effet(bus, effet_id):
    """Définit un effet unique."""
    bus.write_byte_data(DRV_ADDR, REG_SEQ_BASE, effet_id)

def definir_sequence(bus, effet_id, repetitions=4):
    """Définit une séquence répétée de l'effet."""
    for i in range(min(repetitions, 8)):
        bus.write_byte_data(DRV_ADDR, REG_SEQ_BASE + i, effet_id)

def jouer_effet(bus, duree=0.3):
    """Déclenche l'effet configuré."""
    bus.write_byte_data(DRV_ADDR, REG_GO, 0x01)
    time.sleep(duree)

def jouer_sequence(bus, effet_id, repetitions=4, duree_par_effet=0.3):
    """Configure et joue une séquence d'effets longs."""
    definir_sequence(bus, effet_id, repetitions)
    jouer_effet(bus, duree=repetitions * duree_par_effet)

def fermer_moteur(bus):
    """Ferme proprement le bus I2C."""
    bus.close()

#  Exemple d'utilisation
if __name__ == "__main__":
    try:
        bus = smbus.SMBus(1)
        init_moteur(bus)
        effet_long = 0x0C  # Choisis un effet soutenu
        jouer_sequence(bus, effet_id=effet_long, repetitions=4, duree_par_effet=0.3)
        print("Séquence haptique jouée avec succès.")
        fermer_moteur(bus)
    except Exception as e:
        print(f"Erreur moteur : {e}")