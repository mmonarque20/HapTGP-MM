import ecran
from smbus2 import SMBus
import time
import displayio
import neoPixel
import feedbackHaptique
import bme280
import veml7700

# Vitesse MÀJ données
REFRESH_INTERVAL = 0.2

# --- Dicionnaire ---
# Angle : (Couleur Texte, Couleur LED, Titre, Fonction de lecture)
MENU_DONNEES = {
    # "lambda:" est une fonction "en attente". Dans ce code, elle donne l'instruction pour
    #  lire la donnée quand on en a de besoin
    0:   (0xFF69B4, (255,105,180), "Température", lambda: f"{bme280.getTemperature():.2f} °C"),
    72:  (0x0032FF, (0,50,255),    "Humidité",    lambda: f"{bme280.getHumidity():.1f} %"),
    144: (0xFFD700, (255,215,0),   "Pression",    lambda: f"{bme280.getPressure():.1f} hPa"),
    216: (0x00C800, (0,200,0),     "Altitude",    lambda: f"{bme280.getAltitude():.1f} m"),
    288: (0xFF0000, (50,0,0),      "Luminosité",  lambda: f"{veml7700.getLuminosite():.1f} lux")
}

def init_modules():
    pixels = neoPixel.init_pixels()
    neoPixel.allumer_tous(pixels, 0, 0, 0)
    display = ecran.init_display()
    
    display.root_group = displayio.Group()
    try: display.auto_refresh = False
    except: pass
    display.refresh()
    
    pwm, bus_magneto = feedbackHaptique.init_feedback_modules()
    return pixels, display, pwm, bus_magneto

def setup_affichage(display, cible, valeur_initiale):
    # Info du dictionnaire
    cfg = MENU_DONNEES.get(cible, (0xFFFFFF, (0,0,0), "", lambda: ""))
    
    group = ecran.refresh_display(display)
    
    # Fond noir
    group.append(ecran.create_background(color=0x000000))

    # Texte et titre
    titre = ecran.create_text(cfg[2], scale=2, x=120, y=75, color=cfg[0], background_color=None)
    text = ecran.create_text(valeur_initiale, scale=3, x=120, y=120, color=cfg[0], background_color=None)
 
    group.append(titre)
    group.append(text)
    display.root_group = group
    return text

def system_donnee():
    pixels, display, pwm, bus_magneto = init_modules()

    current_cible = None
    text_obj = None
    last_refresh = 0
    haptic_triggered = False

    # Boucle principale
    try:
        with SMBus(bus_magneto) as bus:
            while True:
                # MOTEUR ET BUZZER
                try:
                    angle = feedbackHaptique.lire_angle(bus)
                    haptic_triggered = feedbackHaptique.feedback(angle, pwm, haptic_triggered)
                except:
                    angle = 0 

                # DÉTECTION CIBLE
                # Marge de 8 degrés
                cible_trouvee = next((c for c in MENU_DONNEES if abs((angle % 360) - c) <= 8), None)
                
                now = time.time()
                need_refresh = False

                # AFFICHAGE
                # Cas 1 : Nouvelle cible
                if cible_trouvee is not None and cible_trouvee != current_cible:
                    
                    # Tentative de lecture capteur
                    try:
                        valeur = MENU_DONNEES[cible_trouvee][3]()
                    except:
                        valeur = "Err" 

                    # Affichage écran
                    text_obj = setup_affichage(display, cible_trouvee, valeur)
                    
                    # Affichage LEDs
                    try:
                        neoPixel.allumer_tous(pixels, *MENU_DONNEES[cible_trouvee][1])
                    except:
                        pass

                    current_cible = cible_trouvee
                    last_refresh = now
                    display.refresh()

                # Cas 2 : Même cible
                elif current_cible is not None:
                    if now - last_refresh >= REFRESH_INTERVAL:
                        
                        try:
                            nouvelle_valeur = MENU_DONNEES[current_cible][3]()
                            
                            if text_obj.text != nouvelle_valeur:
                                text_obj.text = nouvelle_valeur
                                need_refresh = True
                        except:
                            pass # Si ça plante, on garde l'ancienne valeur
                        
                        last_refresh = now

                # ENVOI ÉCRAN
                if need_refresh:
                    display.refresh()

    except KeyboardInterrupt:
        neoPixel.eteindre_pixels(pixels)
        print("Fin.")

if __name__ == "__main__":
    system_donnee()