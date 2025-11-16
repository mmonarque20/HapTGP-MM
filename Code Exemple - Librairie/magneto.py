"""
Cette librairie permet de calibrer le magnétomètre au 0 de notre choix 
C'est aussi un programme permettant de tester le module MT6701
 """

import time
import smbus  

# --- Constantes I2C et Registres ---
I2C_BUS_NUMBER = 1
DEVICE_ADDRESS = 0x06
REGISTER_DIR = 0x29
REGISTER_ANGLE_MSB = 0x03
REGISTER_ANGLE_LSB = 0x04

# --- Variables Globales d'État ---
offset_angle = 0.0
filtered_angle = 0.0

def initMagneto(bus):
    """Calibre le zéro du capteur en lisant l'angle actuel comme référence."""
    global offset_angle
    global filtered_angle

    print("Place ton capteur à la position de référence et appuie sur Entrée pour calibrer le zéro.")
    input()

    # Configuration pour lecture CW
    dir_val = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_DIR)
    dir_val |= 0b00000010
    bus.write_byte_data(DEVICE_ADDRESS, REGISTER_DIR, dir_val)

    # Lecture MSB et LSB
    msb = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_MSB)
    lsb = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_LSB)

    # Calcul de l'angle brut
    raw = (msb << 6) | (lsb >> 2)
    offset_angle = raw * (360.0 / 16384.0) #16384 = 14 bits = résolution du capteur

    print(f"Zéro calibré à {offset_angle:.1f}°")
    filtered_angle = 0.0

def getAngle(bus):
    """Retourne l'angle brut, corrigé et filtré."""
    global filtered_angle

    # Lecture brute
    dir_val = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_DIR)
    dir_val |= 0b00000010
    bus.write_byte_data(DEVICE_ADDRESS, REGISTER_DIR, dir_val)

    msb = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_MSB)
    lsb = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_LSB)

    raw = (msb << 6) | (lsb >> 2)
    angle_brut = raw * (360.0 / 16384.0)

    # Correction d'offset
    angle_corrige = (angle_brut - offset_angle + 360) % 360

    # Filtrage circulaire
    prev = filtered_angle
    new = angle_corrige
    alpha = 0.1
    seuil = 30

    delta = (new - prev + 540) % 360 - 180

    if abs(delta) > seuil:
        filtered_angle = new
    else:
        filtered_angle = (prev + alpha * delta) % 360

    return angle_brut, angle_corrige, filtered_angle


# --- Test local ---
if __name__ == "__main__":
    try:
        bus = smbus.SMBus(I2C_BUS_NUMBER)
        initMagneto(bus)
        while True:
            angle_brut, angle_corrige, angle_filtre = getAngle(bus)
            print(f"Brut : {angle_brut:.1f}° | Corrigé : {angle_corrige:.1f}° | Filtré : {angle_filtre:.1f}°")
            time.sleep(0.5)
    except Exception as e:
        print(f"Erreur d'exécution : {e}")