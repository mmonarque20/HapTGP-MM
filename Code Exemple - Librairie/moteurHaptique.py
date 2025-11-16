import time
import smbus

DRV_ADDR = 0x5A
bus = smbus.SMBus(1)

# Registres
REG_MODE = 0x01
REG_GO = 0x0C
REG_SEQ0 = 0x04
REG_OVERDRIVE = 0x0D
REG_LIB_SEL = 0x03

# Fonctions

def initialiser_driver():
    """Initialise le pilote DRV2605L."""
    bus.write_byte_data(DRV_ADDR, REG_MODE, 0x00)       # Internal Trigger Mode
    bus.write_byte_data(DRV_ADDR, REG_LIB_SEL, 0x01)    # Librairie 1 (ERM)
    bus.write_byte_data(DRV_ADDR, REG_OVERDRIVE, 0xFF)  # Overdrive max

def definir_effet(effet_id: int):
    """Définit l'effet à jouer."""
    bus.write_byte_data(DRV_ADDR, REG_SEQ0, effet_id)

def jouer_effet():
    """Lance l'effet configuré et attend 1 seconde."""
    bus.write_byte_data(DRV_ADDR, REG_GO, 0x01)
    time.sleep(1)

# Programme Principal

if __name__ == "__main__":
    initialiser_driver()

    # Effet n°1 : Strong Click (dans la librairie 1)
    EFFET_FORT_CLICK = 0x01
    definir_effet(EFFET_FORT_CLICK)

    jouer_effet()

    # Exemple de second effet
    # definer_effet(0x0A) # Effet 10 : Transition Click/Pop
    # jouer_effet()