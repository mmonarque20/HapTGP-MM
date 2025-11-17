"""
Programme permettant d'afficher les données du Bme280 et du veml7700 sur l'écran GC9A01A
"""

import time
import bme280 # Librairie à partir du programme bme280.py
import veml7700 # Librairie à partir du programme veml7700.py
import displayio
import ecran  # Librairie fait à partir du code exemple du programme ecran.py

# Initialisation de l’écran
display = ecran.init_display()

# Boucle principale
try:
    while True:
        # Réinitialiser l’écran (efface tout)
        group = ecran.refresh_display(display)

        # Fond et cercle
        group.append(ecran.create_background(color=0x500030))
        group.append(ecran.create_circle(x=120, y=120, radius=100, color=0xFFFFFF))

        # Affichage des données
        group.append(ecran.create_text(f"{bme280.getTemperature():.1f} °C", scale=2, x=80, y=60, color=0x505000))
        group.append(ecran.create_text(f"{bme280.getHumidity():.1f} %", scale=2, x=80, y=80, color=0x00FFFF))
        group.append(ecran.create_text(f"{bme280.getPressure():.1f} hPa", scale=2, x=80, y=100, color=0xFF00FF))
        group.append(ecran.create_text(f"{bme280.getAltitude():.1f} m", scale=2, x=80, y=120, color=0x554002))
        group.append(ecran.create_text(f"{veml7700.getLuminosite():.1f} lux", scale=2, x=80, y=140, color=0x00FF00))
        display.root_group = group

        time.sleep(5)
except KeyboardInterrupt:
    print("\nArrêt du programme.")
    ecran.sleep_display(display)
    time.sleep(0.5)
