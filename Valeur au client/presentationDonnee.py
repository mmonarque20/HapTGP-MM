# Code permettant d'afficher les données selon l'angle du magnétomètre et avoir un feedback du moteur et du buzzer

import ecran
from smbus2 import SMBus
import time
import neoPixel
import feedbackHaptique
import bme280
import veml7700

REFRESH_INTERVAL = 1 # seconde

# --- Initialisation ---

def init_modules():
    pixels = neoPixel.init_pixels()
    neoPixel.allumer_tous(pixels, 0, 0, 0)
    
    display = ecran.init_display()
    pwm, bus_magneto = feedbackHaptique.init_feedback_modules()
    return pixels, display, pwm, bus_magneto

# --- Affichage par cible ---
def affichage_par_cible(display, cible):
    group = ecran.refresh_display(display)
    group.append(ecran.create_background(color=0xFFFFFF))

    if cible == 0:
        circle_color = 0xFF69B4
    elif cible == 72:
        circle_color = 0x0032FF
    elif cible == 144:
        circle_color = 0xFFD700
    elif cible == 216:
        circle_color = 0x00C800
    elif cible == 288:
        circle_color = 0xFF0000
    else:
        circle_color = 0xFFFFFF

    group.append(ecran.create_circle(x=120, y=120, radius=100, color=circle_color))
    titre = ecran.create_text("", scale=2, x=120, y=75, color=circle_color, background_color=None)
    text = ecran.create_text("", scale=3, x=120, y=120, color=circle_color, background_color=None)
    group.append(titre)
    group.append(text)

    display.root_group = group
    return text, titre   

# --- Update du texte --- 
def update_text(text,titre,cible):
    text.color = 0xFFFFFF
    titre.color = 0xFFFFFF
    if cible == 0:
        titre.text = "Température"
        text.text = f"{bme280.getTemperature():.1f} °C"      
    elif cible == 72:
        titre.text = "Humidité"
        text.text = f"{bme280.getHumidity():.1f} %"
    elif cible == 144:
        titre.text = "Pression"
        text.text = f"{bme280.getPressure():.1f} hPa"       
    elif cible == 216:
        titre.text = "Altitude"
        text.text = f"{bme280.getAltitude():.1f} m"        
    elif cible == 288:
        titre.text = "Luminosité"
        text.text = f"{veml7700.getLuminosite():.1f} lux"
        

   

# --- Couleur des DELs par cible ---
def couleur_pixels(pixels,cible):
    if cible == 0:
        neoPixel.allumer_tous(pixels,255,105,180)
    elif cible == 72:
        neoPixel.allumer_tous(pixels,0, 50, 255)
    elif cible == 144:
        neoPixel.allumer_tous(pixels,255, 215,0)
    elif cible == 216:
        neoPixel.allumer_tous(pixels,0,200,0)
    elif cible == 288:
        neoPixel.allumer_tous(pixels,255, 0, 0)


# --- Programme principal ---

def system_donnee(pixels=None, display=None, pwm=None):
    
    # DÉTECTION DU MODE
    mode_autonome = False
    bus_magneto = 1

    if display is None:
        # CAS 1 : MODE AUTONOME (TEST)
        print ("---Mode Autonome (Test) : Initialisation---")
        pixels, display, pwm, bus_magneto = init_modules()
        mode_autonome = True
    else:
        # CAS 2 : MODE INTÉGRÉ
        print ("---Mode Intégré : Utilisation du menu---")
        mode_autonome = False
    
    # Variables locales
    haptic_triggered = False
    last_refresh = 0
    current_cible = None
    text_obj = None
    titre_obj = None

    # BOUCLE PRINCIPALE
    try:
        with SMBus(bus_magneto) as bus:
            while True:
                current_angle = feedbackHaptique.lire_angle(bus)
                haptic_triggered = feedbackHaptique.feedback(current_angle, pwm, haptic_triggered)

                # Détection de la cible
                cible = None
                for c in [0, 72, 144, 216, 288]:
                    if abs((current_angle % 360) - c) <= 5:
                        cible = c
                        break

                now = time.time()
                # ---GESTION AFFICHAGE---
                if cible is not None:
                    # --- Cas 1 : nouvelle cible ---
                    if cible != current_cible:
                        text_obj, titre_obj = affichage_par_cible(display, cible)
                        couleur_pixels(pixels, cible)
                        current_cible = cible
                        last_refresh = now
                        update_text(text_obj,titre_obj,cible)

                    # --- Cas 2 : même cible ---
                    elif now - last_refresh >= REFRESH_INTERVAL:
                        update_text(text_obj,titre_obj, cible)
                        last_refresh = now

                else:
                    # Pas de cible : On garde l'affichage précédent à jour
                    if current_cible is not None and now - last_refresh >= REFRESH_INTERVAL:
                        update_text(text_obj,titre_obj, current_cible)
                        couleur_pixels(pixels, current_cible)
                        last_refresh = now

                print(f"Angle : {current_angle:.1f}°")
                #time.sleep(0.05)

    except KeyboardInterrupt:
        print("Arrêt demandé.")

        if mode_autonome:
            print("Arrêt complet (Autonome)")
            neoPixel.eteindre_pixels(pixels)
            ecran.sleep_display(display)
        else:
            print ("Retour au menu principal")
            neoPixel.eteindre_pixels(pixels)

if __name__ == "__main__":
    system_donnee()

