from smbus2 import SMBus
import time, displayio,RPi.GPIO as GPIO, board, cst816
import bme280, veml7700, neoPixel, ecran, horloge, feedbackHaptique, buzzer # Module Personnel
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo

# --- CONFIGURATION ET CONSTANTES ---
TOUCH_RST_PIN = 17 
GESTURE_SWIPE_UP, GESTURE_SWIPE_LEFT, GESTURE_SWIPE_RIGHT = 2, 3, 4

HOST_TB = "206.167.80.224"  # (tb-io.claurendeau.qc.ca)
TOKEN_TB = "wzRVz5UzTs6SvKQIuR2U"

VITESSE_CYCLE_MENU = 30 # Vitesse de cycle des couleurs LEDs
LUMINOSITE_LEDS= 0.2    # Intensité des LEDs
NOIR, BLANC, ROUGE, VERT, JAUNE, BLEU = 0x000000, 0xFFFFFF, 0xFF0000, 0x00B400, 0xFFC800, 0x0000FF # Code de couleurs pour l'écran (HEX)

# --- DICTIONNAIRE DE DONNÉES ---
#Ce dictionnaire configure le comportement du menu "DATA" selon l'angle du magnétomètre
# Angle : (Couleur Texte, Couleur LED, Titre à afficher, Fonction de lecture du capteur)
MENU_DONNEES = {
    0:   (0xFF69B4, (255,105,180), "Temperature", lambda: f"{bme280.getTemperature():.2f} C"),
    72:  (0x0032FF, (0,50,255),    "Humidite",    lambda: f"{bme280.getHumidity():.1f} %"),
    144: (0xFFD700, (255,215,0),   "Pression",    lambda: f"{bme280.getPressure():.1f} hPa"),
    216: (0x00C800, (0,200,0),     "Altitude",    lambda: f"{bme280.getAltitude():.1f} m"),
    288: (0xFF0000, (50,0,0),      "Luminosite",  lambda: f"{veml7700.getLuminosite():.1f} lux")
}

# --- FONCTION UTILITAIRE ---    
def color_wheel(pos):
    """ Génère une couleur (R, G, B)en fonction d'une position (0 à 255)."""
    if pos < 0 or pos > 255: return (0, 0, 0)   
    if pos < 85: return (int(pos * 3), int(255 - pos * 3), 0) # Rouge -> Vert
    elif pos < 170: pos -= 85; return (int(255 - pos * 3), 0, int(pos * 3)) # Vert -> Bleu
    else: pos -= 170; return (0, int(pos * 3), int(255 - pos * 3)) # Bleu -> Rouge

# --- INTERFACES GRAPHIQUES --- 
def setup_ui_loading():
    """ Crée l'écran de chargement """
    group = displayio.Group()
    group.append(ecran.create_background(color=NOIR))
    group.append(ecran.create_text("Initialisation...", scale=2, x=120, y=120, color=BLANC,background_color=NOIR))
    group.append(ecran.create_text("Info dans le terminal", scale=1, x=120, y=210, color=BLANC,background_color=NOIR)) # Instruction pour l'utilisateur
    return group

def setup_ui_menu():
    """ Crée l'écran principal (MENU) """
    group = displayio.Group()
    group.append(ecran.create_background(color=NOIR))   
    group.append(ecran.create_text("HAPTGP MM", scale=3, x=120, y=50, color=ROUGE, background_color=NOIR))
    group.append(ecran.create_text("Let's go!", scale=2, x=120, y=180, color=VERT, background_color=NOIR))
    group.append(ecran.create_text("Swipe DROITE = Données", scale=1, x=120, y=210, color=BLANC, background_color=NOIR)) # Instruction pour l'utilisateur
    lbl_date = ecran.create_text("YYYY-MM-DD", scale=2, x=120, y=100, color=JAUNE, background_color=NOIR)
    lbl_heure = ecran.create_text("00:00:00", scale=3, x=120, y=140, color=BLEU, background_color=NOIR)
    group.append(lbl_date); group.append(lbl_heure)
    print("Setup Menu Complété")
    return group, lbl_date, lbl_heure

def setup_ui_data():
    """ Interface des DONNÉES"""
    group = displayio.Group()
    group.append(ecran.create_background(color=NOIR))
    titre_obj = ecran.create_text("", scale=2, x=120, y=75, color=0xFFFFFF, background_color=NOIR)   # Titre des capteurs (Température, Pression ...)
    valeur_obj = ecran.create_text("", scale=3, x=120, y=120, color=0xFFFFFF, background_color=NOIR) # Valeur des capteurs (Température, Pression ...)
    group.append(titre_obj); group.append(valeur_obj)   
    group.append(ecran.create_text("Swipe GAUCHE = Menu", scale=1, x=120, y=210, color=BLANC, background_color=NOIR )) # Instruction de Navigation
    group.append(ecran.create_text("Swipe HAUT = Envoie vers TB", scale=1, x=120, y=190, color=BLANC, background_color=NOIR ))    
    print("Setup Data Complété")
    return group, titre_obj, valeur_obj

# --- INITIALISATION ---
def Initialisation_modules():
    """ Initialise écran, capteurs, LEDs, haptique et interfaces """    
    display = None
    try:
        display = ecran.init_display(); display.auto_refresh = False    # Écran
        display.root_group = setup_ui_loading(); display.refresh()
    except Exception as e :
        print(f"Erreur Écran : {e}"); return None 
    GPIO.setmode(GPIO.BCM); GPIO.setup(TOUCH_RST_PIN, GPIO.OUT); GPIO.output(TOUCH_RST_PIN, GPIO.HIGH); time.sleep(0.1) # RST Touch Screen
    try: 
        touch = cst816.CST816(board.I2C())  # Touch Screen
        pixels = neoPixel.init_pixels(); neoPixel.eteindre_pixels(pixels) # DELs
        rtc = horloge.init_horloge()   # Horloge 
        pwm, bus_magneto = feedbackHaptique.init_feedback_modules()  # Moteur, Magnétomètre    
        grp_menu, lbl_date, lbl_heure = setup_ui_menu() # Prépare l'interface Menu en mémoire
        grp_data, lbl_titre, lbl_valeur = setup_ui_data()  # Prépare l'interface Données en mémoire
        print ("Initialisation des Modules Complété"); time.sleep(1)
        return (touch, pixels, display, pwm, bus_magneto, rtc, grp_menu, lbl_date, lbl_heure,grp_data, lbl_titre, lbl_valeur) 
    except Exception as e:
        print(f"Erreur Initialisation: {e}"); return None

def connect_TB(host, token):
    """ Gère la connexion au serveur MQTT ThingsBoard """
    try:
        client = TBDeviceMqttClient(host, username=token); client.connect()
        while not client.is_connected():
            print("Connexion à ThingsBoard en cours..."); time.sleep(1)
        print("Connecté à ThingsBoard !"); return client
    except Exception as e:
        print(f"Erreur TB: {e}"); return None

# --- PROGRAMME PRINCIPAL --- 
if __name__ == "__main__":
    sys = Initialisation_modules()
    if sys :
        (touch, pixels, display, pwm, bus_magneto, rtc, grp_menu, lbl_date, lbl_heure, grp_data, lbl_titre, lbl_valeur) = sys
        client = connect_TB(HOST_TB, TOKEN_TB)
        mode_actuel = "MENU"; last_sec = 0; current_data_target = None # Configuration de l'état initial, Aucun capteur (Donnée) sélectionnée au départ
        display.root_group = grp_menu; display.refresh() # Affichage du Menu
        neoPixel.allumer_tous(pixels,0,255,0) # "Prêt"
        try: buzzer.jouer_intro(pwm) # Musique d'introduction. Thème : Mario
        except Exception as e:print(f"Erreur audio : {e}")
        try:
            with SMBus(bus_magneto) as bus:
                print("---DÉMARRAGE PROGRAMME---")
                while True:
                    now = time.monotonic()  # Récupère le temps actuel
                    # --- TOUCH SCREEN --- 
                    gesture = 0
                    if touch.get_touch():
                        gesture = touch.get_gesture()   
                        while touch.get_touch():
                            ges = touch.get_gesture()
                            if ges != 0:gesture = ges
                            time.sleep(0.01)
                        print(f"Action Tactile terminée. Geste ID: {gesture}")
                        # ---  NAVIGATION ---
                        if mode_actuel == "MENU" and gesture == GESTURE_SWIPE_RIGHT: # On est dans le menu et on swipe à droite
                                print(">> Changement : Interface DONNÉES")
                                mode_actuel = "DATA"; display.root_group = grp_data   # Change l'état et l'image affichée
                                buzzer.jouer_musique(pwm); feedbackHaptique.jouer_haptique(bus); time.sleep(0.3) # Feedback son et vibration
                        elif mode_actuel == "DATA":    # On est dans le mode Data
                            if gesture == GESTURE_SWIPE_LEFT:
                                print("<< Changement : Interface MENU")
                                mode_actuel = "MENU"; display.root_group = grp_menu
                                neoPixel.eteindre_pixels(pixels); current_data_target = None 
                                buzzer.jouer_musique(pwm); feedbackHaptique.jouer_haptique(bus); time.sleep(0.3)     
                            elif gesture == GESTURE_SWIPE_UP:
                                print("^^ Envoi vers ThingsBoard")
                                neoPixel.allumer_tous(pixels, 255, 200, 0)
                                try:
                                    telemetry = {
                                        "Temperature": float(bme280.getTemperature()), 
                                        "Humidite": float(bme280.getHumidity()), 
                                        "Pression": float(bme280.getPressure()), 
                                        "Altitude": float(bme280.getAltitude()), 
                                        "Luminosite": float(veml7700.getLuminosite())
                                    }
                                    if client:
                                        result = client.send_telemetry(telemetry)
                                        status = result.get()
                                        if status == TBPublishInfo.TB_ERR_SUCCESS:
                                            print(f"Succès envoi TG : {telemetry}")
                                            neoPixel.allumer_tous(pixels, 0, 255 ,0)
                                            buzzer.bip(pwm,2000,0.05); time.sleep(0.1); buzzer.bip(pwm, 2000, 0.05)    
                                        else:
                                            print(f"Échec envoi TB. Code: {str(result)}")
                                            neoPixel.allumer_tous(pixels,255,0,0)
                                    else:
                                        print("Erreur : Client non connecté")
                                        neoPixel.allumer_tous(pixels,255,0,0)
                                
                                except Exception as e :
                                    print(f"Erreur lecture capteurs ou envoi : {e}")
                                    neoPixel.allumer_tous(pixels,255,0,0)

                                time.sleep(0.5)
                                current_data_target = None

                    # --- MAJ DE L'AFFICHAGE (Selon le mode) ---
                    if mode_actuel == "MENU":
                        # Met à jour l'heure une fois par seconde
                        if int(now) != last_sec:    
                            lbl_heure.text = horloge.get_heure(rtc)
                            lbl_date.text = horloge.get_date(rtc)
                            display.refresh()
                            last_sec = int(now)
                        try:
                            # Animation des DELS
                            position_cycle = int(now * VITESSE_CYCLE_MENU) %256
                            r, g, b = color_wheel(position_cycle)
                            neoPixel.allumer_tous(pixels, int(r*LUMINOSITE_LEDS), int(g*LUMINOSITE_LEDS), int(b*LUMINOSITE_LEDS))
                        except Exception as e:
                            print(f"Erreur LED: {e}")
                    
                    elif mode_actuel == "DATA":
                        angle_mesure = feedbackHaptique.lire_angle(bus) # Lit la position du bouton rotatif
                        closest_key = min(MENU_DONNEES.keys(), key=lambda x: abs(x - angle_mesure)) # Trouver la clé la plus proche dans le dictionnaire
                        (txt_col, led_col, title_str, func_read) = MENU_DONNEES[closest_key]    # Récupérer l'info associé à cet angle
                        if current_data_target != closest_key: # Si on change de cible, on met à jour le titre et les couleurs
                            current_data_target = closest_key
                            lbl_titre.text = title_str
                            lbl_titre.color = txt_col
                            neoPixel.allumer_tous(pixels, led_col[0], led_col[1], led_col[2])   
                        try:
                            lbl_valeur.text = func_read() # Lecture de la valeur du capteur (via la fct lambda) et l'affiche
                        except:
                            lbl_valeur.text = "Err"
                    display.refresh()
                    time.sleep(0.02)
        
        except KeyboardInterrupt:
            print("\nArrêt du programme")
            neoPixel.eteindre_pixels(pixels)
            try:
                group_off = displayio.Group()
                group_off.append(ecran.create_background(color=NOIR))
                display.root_group = group_off
                display.refresh()
                time.sleep(0.5)
            except Exception as e:
                print(f"Erreur fermeture écran: {e}")
            if client:
                client.disconnect()
            GPIO.cleanup()
        except Exception as e:
            print(f"Erreur fatale : {e}")

            




                                                                





