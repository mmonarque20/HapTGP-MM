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

# --- Dictionnaire ---
# Angle : (Couleur Texte, Couleur LED, Titre, Fonction de lecture)
MENU_DONNEES = {
    0:   (0xFF69B4, (255,105,180), "Temperature", lambda: f"{bme280.getTemperature():.2f} C"),
    72:  (0x0032FF, (0,50,255),    "Humidite",    lambda: f"{bme280.getHumidity():.1f} %"),
    144: (0xFFD700, (255,215,0),   "Pression",    lambda: f"{bme280.getPressure():.1f} hPa"),
    216: (0x00C800, (0,200,0),     "Altitude",    lambda: f"{bme280.getAltitude():.1f} m"),
    288: (0xFF0000, (50,0,0),      "Luminosite",  lambda: f"{veml7700.getLuminosite():.1f} lux")
}

def init_modules():
    pixels = neoPixel.init_pixels()
    neoPixel.allumer_tous(pixels, 0, 0, 0)
    display = ecran.init_display()
    
    # On s'assure que l'auto_refresh est off pour la performance
    try: display.auto_refresh = False
    except: pass
    
    pwm, bus_magneto = feedbackHaptique.init_feedback_modules()
    return pixels, display, pwm, bus_magneto

def initialiser_interface(display):
    """
    Crée le groupe et les objets textes UNE SEULE FOIS.
    Retourne les objets (titre, valeur) pour qu'on puisse les modifier plus tard.
    """
    # Groupe principal
    main_group = displayio.Group()
    
    # Fond noir 
    bg = ecran.create_background(color=0x000000)
    main_group.append(bg)

    # Création des objets textes 
    # On initialise avec une couleur blanche temporaire, elle changera tout de suite
    titre_obj = ecran.create_text("", scale=2, x=120, y=75, color=0xFFFFFF, background_color=None)
    valeur_obj = ecran.create_text("", scale=3, x=120, y=120, color=0xFFFFFF, background_color=None)
    
    # Ajout au groupe
    main_group.append(titre_obj)
    main_group.append(valeur_obj)
    
    # Affichage du groupe
    display.root_group = main_group
    display.refresh()
    
    return titre_obj, valeur_obj

def system_donnee():
    pixels, display, pwm, bus_magneto = init_modules()

    # Création de l'interface AVANT la boucle 
    titre_label, valeur_label = initialiser_interface(display)

    current_cible = None
    last_refresh = 0
    haptic_triggered = False

    try:
        with SMBus(bus_magneto) as bus:
            while True:
                # --- MOTEUR ET BUZZER ---
                try:
                    angle = feedbackHaptique.lire_angle(bus)
                    haptic_triggered = feedbackHaptique.feedback(angle, pwm, haptic_triggered)
                except:
                    pass

                # --- DÉTECTION CIBLE ---
                # On cherche si l'angle correspond à une entrée du menu (marge 8 degrés)
                cible_trouvee = next((c for c in MENU_DONNEES if abs((angle % 360) - c) <= 5), None)
                
                now = time.time()
                need_refresh = False

                # --- LOGIQUE D'AFFICHAGE ---
                
                # CAS 1 : Changement de menu (On change Titre, Couleur et Valeur)
                if cible_trouvee is not None and cible_trouvee != current_cible:
                    
                    # Récupération de la config
                    cfg = MENU_DONNEES[cible_trouvee]
                    color_hex = cfg[0]
                    led_rgb = cfg[1]
                    titre_str = cfg[2]
                    func_valeur = cfg[3]

                    # Mise à jour des LEDs
                    try: neoPixel.allumer_tous(pixels, *led_rgb)
                    except: pass

                    # Mise à jour de l'ÉCRAN
                    try:
                        # Titre
                        if titre_label.text != titre_str:
                            titre_label.text = titre_str
                        
                        # Couleur des deux textes
                        titre_label.color = color_hex
                        valeur_label.color = color_hex # Suppose que ton objet texte a un attribut .color
                        
                        # On calcule et change la valeur
                        nouvelle_val = func_valeur()
                        valeur_label.text = nouvelle_val
                        
                        need_refresh = True
                    except Exception as e:
                        print(f"Erreur update ecran: {e}")
                        valeur_label.text = "Err"

                    current_cible = cible_trouvee
                    last_refresh = now

                # CAS 2 : Même menu, on met à jour seulement la valeur périodiquement
                elif current_cible is not None:
                    if now - last_refresh >= REFRESH_INTERVAL:
                        try:
                            nouvelle_valeur = MENU_DONNEES[current_cible][3]()
                            
                            # On ne touche à l'écran que si le texte a changé
                            if valeur_label.text != nouvelle_valeur:
                                valeur_label.text = nouvelle_valeur
                                need_refresh = True
                        except:
                            pass 
                        
                        last_refresh = now

                # Envoi à l'écran seulement si nécessaire
                if need_refresh:
                    display.refresh()

    except KeyboardInterrupt:
        neoPixel.eteindre_pixels(pixels)
        print("Fin.")

if __name__ == "__main__":
    system_donnee()