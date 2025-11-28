import time
import displayio
import math 

# Modules
import horloge
import ecran
import neoPixel
import buzzer

# --- CONSTANTES ---
ROUGE = (100, 0, 0)
JAUNE = (100, 100, 0)
BLEU = (0, 0, 100)
VERT_M = (140, 159, 16) 

COULEURS_LEDS = [ROUGE, JAUNE, BLEU]

# --- REGLAGE VITESSE ---
VITESSE_LEDS = 3.0

DELAI_CHECK_RAPIDE = 0.1 
DELAI_PAUSE_LONGUE = 0.8  

# --- FONCTIONS ---

def setup(display):
    try: display.auto_refresh = False
    except AttributeError: pass 

    # Fond
    group = displayio.Group()
    group.append(ecran.create_background(color=0xFFFFFF))
    
    # Texte statique
    group.append(ecran.create_text("HapTGP MM", scale=3, x=120, y=50, color=0xFF0000))
    lbl_instr = ecran.create_text("Tap pour commencer :)", scale=1, x=120, y=170, color=VERT_M, background_color=0xFFFFFF)
    group.append(lbl_instr)
    
    # Texte dynamique
    lbl_date = ecran.create_text("YYYY-MM-DD", scale=2, x=120, y=110, color=0x000000)
    lbl_heure = ecran.create_text("00:00:00", scale=3, x=120, y=140, color=0x0000FF)
    
    group.append(lbl_date)
    group.append(lbl_heure)

    display.root_group = group
    try: display.refresh()
    except: pass

    # État DELS et horloge
    etat_led = {'color_index': 0}
    etat_horloge = {'prochain_check': 0}

    return lbl_date, lbl_heure, lbl_instr, etat_led, etat_horloge



def update(rtc, pixels, now, lbl_date, lbl_heure, etat_led, etat_horloge):
    needs_refresh = False

    # --- 1. Gestion Horloge ---
    if now >= etat_horloge['prochain_check']:
        try:
            heure_txt = horloge.get_heure(rtc)
            if lbl_heure.text != heure_txt:
                lbl_heure.text = heure_txt
                lbl_date.text = horloge.get_date(rtc)
                etat_horloge['prochain_check'] = now + DELAI_PAUSE_LONGUE
                needs_refresh = True 
            else:
                etat_horloge['prochain_check'] = now + DELAI_CHECK_RAPIDE
        except:
            etat_horloge['prochain_check'] = now + DELAI_CHECK_RAPIDE

    # --- 2. Gestion LEDs (RESPIRATION MATHÉMATIQUE) ---
    
    # Calcul de l'onde (valeur entre -1 et 1)
    onde = math.sin(now * VITESSE_LEDS)
    
    # Transformation en luminosité (0.0 à 1.0)
    luminosite_brute = (onde + 1) / 2
    
    # Luminosité Finale
    luminosite_finale = luminosite_brute ** 3 

    # Changement de couleur
    if luminosite_finale < 0.005: 
        cycle = int(now / (3.14159 * 2 / VITESSE_LEDS))
        etat_led['color_index'] = cycle % len(COULEURS_LEDS)

    # Application
    r_base, g_base, b_base = COULEURS_LEDS[etat_led['color_index']]
    
    # Calcule couleur finale atténuée
    r = int(r_base * luminosite_finale)
    g = int(g_base * luminosite_finale)
    b = int(b_base * luminosite_finale)

    try:
        neoPixel.allumer_tous(pixels, r, g, b)
    except:
        pass
            
    return needs_refresh


# --- MAIN ---
if __name__=="__main__":
    print("--- Mode Autonome ---")
    pixels = neoPixel.init_pixels()
    pwm = buzzer.init_buzzer()
    display = ecran.init_display()
    rtc = horloge.init_horloge()

    try:
        lbl_date, lbl_heure, lbl_instr, etat_led, etat_horloge = setup(display)
        buzzer.jouer_intro(pwm)

        while True:
            now = time.monotonic()
            ecran_a_change = update(rtc, pixels, now, lbl_date, lbl_heure, etat_led, etat_horloge)
            
            if ecran_a_change:
                try: display.refresh()
                except: pass
            pass

    except KeyboardInterrupt:
        print("\nArrêt.")
    finally:
        neoPixel.eteindre_pixels(pixels)
        ecran.sleep_display(display)
        if hasattr(pwm, 'deinit'): pwm.deinit()