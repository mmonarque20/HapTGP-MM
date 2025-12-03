import time
import displayio
import horloge
import ecran
import neoPixel
import buzzer

# --- RÉGLAGES ---
LUMINOSITE = 0.2     # Puissance des LEDs
VITESSE_CYCLE = 30   # Plus ce chiffre est grand, plus les couleurs changent vite

# --- COULEURS TEXTE (HEX) ---
ROUGE_TXT = 0xFF0000
VERT_TXT  = 0x00B400
JAUNE_TXT = 0xFFC800
BLEU_TXT  = 0x0000FF
BLANC_TXT = 0xFFFFFF
NOIR_FOND = 0x000000

def setup_ecran(display):
    """Prépare l'affichage statique et dynamique."""
    try: display.auto_refresh = False
    except: pass 

    group = displayio.Group()
    group.append(ecran.create_background(color=NOIR_FOND))
    
    # Textes fixes
    group.append(ecran.create_text("HAPTGP MM", scale=3, x=120, y=50, color=ROUGE_TXT, background_color=NOIR_FOND))
    
    lbl_quote = ecran.create_text("Let's go!", scale=2, x=120, y=180, color=VERT_TXT, background_color=NOIR_FOND)
    lbl_instr = ecran.create_text("tap pour commencer :)", scale=1, x=120, y=210, color=BLANC_TXT, background_color=NOIR_FOND)
    group.append(lbl_quote)
    group.append(lbl_instr)
    
    # Date et Heure
    lbl_date = ecran.create_text("YYYY-MM-DD", scale=2, x=120, y=100, color=JAUNE_TXT, background_color=NOIR_FOND)
    lbl_heure = ecran.create_text("00:00:00", scale=3, x=120, y=140, color=BLEU_TXT, background_color=NOIR_FOND)
    
    group.append(lbl_date)
    group.append(lbl_heure)
    
    display.root_group = group
    display.refresh()
    
    return lbl_date, lbl_heure

def color_wheel(pos):
    """
    Génère une couleur en fonction d'une position (0 à 255).
    Ordre demandé : VERT -> ROUGE -> BLEU
    """
    # S'assurer que la position est entre 0 et 255
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    
    # 1er tiers : VERT vers ROUGE
    if pos < 85:
        return (int(pos * 3), int(255 - pos * 3), 0)
    
    # 2ème tiers : ROUGE vers BLEU
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    
    # 3ème tiers : BLEU vers VERT (retour au début)
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))

def menu_run():    
    pixels = neoPixel.init_pixels()
    pwm = buzzer.init_buzzer()
    display = ecran.init_display()
    rtc = horloge.init_horloge()

    try:
        lbl_date, lbl_heure = setup_ecran(display)
        try: buzzer.jouer_intro(pwm)
        except: pass

        last_sec = 0
        
        while True:
            now = time.monotonic()
            
            # --- HORLOGE ---
            if int(now) != last_sec:
                lbl_heure.text = horloge.get_heure(rtc)
                lbl_date.text = horloge.get_date(rtc)
                display.refresh()
                last_sec = int(now)

            # --- LEDS (Flux continu) ---
            # On transforme le temps en une position de 0 à 255
            # VITESSE_CYCLE permet d'accélérer ou ralentir le défilement
            position_cycle = int(now * VITESSE_CYCLE) % 256
            
            r, g, b = color_wheel(position_cycle)
            
            neoPixel.allumer_tous(pixels, int(r*LUMINOSITE), int(g*LUMINOSITE), int(b*LUMINOSITE))

            time.sleep(0.02) 

    except KeyboardInterrupt:
        print("\nArrêt.")
        neoPixel.eteindre_pixels(pixels)
        ecran.sleep_display(display)
        try: pwm.deinit()
        except: pass

if __name__=="__main__":
    menu_run()