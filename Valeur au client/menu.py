import time
import displayio

# Modules
import horloge
import ecran
import neoPixel
import buzzer

# --- CONSTANTES ---
ROUGE = (255, 0, 0)
JAUNE = (255, 255, 0)
BLEU = (0, 0, 255)
VERT_M = (140, 159, 16) 

COULEURS_LEDS = [ROUGE, JAUNE, BLEU]

# Timings
DELAI_LEDS = 0.05       
DELAI_CHECK_RAPIDE = 0.1 
DELAI_PAUSE_LONGUE = 0.8  

# --- FONCTIONS ---

def setup(display):
    """
    Prépare l'affichage graphique initial.
    """
    try:
        display.auto_refresh = False
    except AttributeError:
        pass 

    group = displayio.Group()

    # Fond
    group.append(ecran.create_background(color=0xFFFFFF))
    
    # Textes 
    group.append(ecran.create_text("HapTGP MM", scale=3, x=120, y=50, color=0xFF0000))
    
    lbl_instr = ecran.create_text("double tap pour commencer :)", scale=1, x=120, y=170, color=VERT_M, background_color=0xFFFFFF)
    group.append(lbl_instr)

    # Zones dynamiques
    lbl_date = ecran.create_text("YYYY-MM-DD", scale=2, x=120, y=100, color=0x000000)
    lbl_heure = ecran.create_text("00:00:00", scale=3, x=120, y=140, color=0x0000FF)
    
    group.append(lbl_date)
    group.append(lbl_heure)

    # Affichage final
    display.root_group = group

    try:
        display.refresh()
    except:
        pass

    etat_led = {'last_time': 0, 'pixel_index': 0, 'color_index': 0}
    etat_horloge = {'prochain_check': 0}

    return lbl_date, lbl_heure, lbl_instr, etat_led, etat_horloge

def update(rtc, pixels, now, lbl_date, lbl_heure, etat_led, etat_horloge):
    """
    Met à jour les données et retourne True si l'écran a besoin d'être rafraîchi.
    """
    needs_refresh = False

    # --- Gestion Horloge ---
    if now >= etat_horloge['prochain_check']:
        try:
            heure_txt = horloge.get_heure(rtc)
            date_txt = horloge.get_date(rtc)
        
            if lbl_heure.text != heure_txt:
                lbl_heure.text = heure_txt
                lbl_date.text = date_txt
                etat_horloge['prochain_check'] = now + DELAI_PAUSE_LONGUE
                needs_refresh = True # L'écran a changé 
            else:
                etat_horloge['prochain_check'] = now + DELAI_CHECK_RAPIDE
        except:
            etat_horloge['prochain_check'] = now + DELAI_CHECK_RAPIDE

    # --- Gestion LEDs ---
    if now - etat_led['last_time'] >= DELAI_LEDS:
        r, g, b = COULEURS_LEDS[etat_led['color_index']]
        try:
            neoPixel.allumer_pixel(pixels, etat_led['pixel_index'], r, g, b)
        except:
            pass
        
        etat_led['pixel_index'] += 1
        etat_led['last_time'] = now

        if etat_led['pixel_index'] >= len(pixels):
            etat_led['pixel_index'] = 0
            etat_led['color_index'] = (etat_led['color_index'] + 1) % len(COULEURS_LEDS) 
            
    return needs_refresh


# --- PROGRAMME PRINCIPAL : MODE AUTONOME ---
if __name__=="__main__":
    print("--- Mode Autonome : Menu ---")

    pixels = neoPixel.init_pixels()
    pwm = buzzer.init_buzzer()
    display = ecran.init_display()
    rtc = horloge.init_horloge()

    # Test LED immédiat
    neoPixel.allumer_pixel(pixels, 0, 0, 0, 50)

    try:
        lbl_date, lbl_heure, lbl_instr, etat_led, etat_horloge = setup(display)
        
        neoPixel.eteindre_pixels(pixels)
        buzzer.jouer_intro(pwm)

        while True:
            now = time.monotonic()
            
            # 1. On met à jour les données (Textes, LEDs)
            ecran_a_change = update(rtc, pixels, now, lbl_date, lbl_heure, etat_led, etat_horloge)
            
            # 2. Si le texte a changé, ON RAFRAÎCHIT L'ÉCRAN MANUELLEMENT

            if ecran_a_change:
                try:
                    display.refresh()
                except Exception as e:
                    print(f"Erreur refresh: {e}")
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nArrêt utilisateur.")

    finally:
        neoPixel.eteindre_pixels(pixels)
        if hasattr(pwm, 'deinit'):
            pwm.deinit()
        print("Arrêt complet.")