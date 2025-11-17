import board
import time
import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
from fourwire import FourWire
from vectorio import Circle
from adafruit_gc9a01a import GC9A01A

# Initialisation de l'écran GCA01A
def init_display():
    displayio.release_displays()
    bus = FourWire(board.SPI(), command=board.D25, chip_select=board.D8, reset=board.D27)
    return GC9A01A(bus, width=240, height=240)

#Réinitialisation de l'écran: pour mise à jour de l'écran
def refresh_display(display):
    new_group = displayio.Group()
    return new_group  

#  Crée un fond coloré avec une palette de deux couleurs
def create_background(color=0xAA00FF):
    bg_bitmap = displayio.Bitmap(240, 240, 1)
    palette = displayio.Palette(1)
    palette[0] = color
    return displayio.TileGrid(bg_bitmap, pixel_shader=palette, x=0, y=0)

# Crée un cercle  centré sur l’écran selon la couleur de ton choix
def create_circle(x=120, y=120, radius=100, color=0xFFFFFF):
    palette = displayio.Palette(1)
    palette[0] = color
    return Circle(pixel_shader=palette, radius=radius, x=x, y=y)

# Crée un groupe de texte avec position et couleur personnalisées
def create_text(text, scale, x, y, color=0xAA00FF):
    group = displayio.Group(scale=scale, x=x, y=y)
    label = Label(terminalio.FONT, text=text, color=color)
    group.append(label)
    return group   

# Affiche la démo complète : fond, cercle, et deux textes
def show_demo(display):
    group = displayio.Group()
    display.root_group = group
    group.append(create_background(color=0x000000))  
    group.append(create_circle(x=120, y=120, radius=100, color=0xFFFFFF))
    group.append(create_text("Hello People!",scale=2, x=50, y=120, color=0x00FF00))
    group.append(create_text("It's Mary :)",scale=2, x=50, y=150, color=0x0000FF))

# Éteint visuellement l’écran 
def sleep_display(display):
    display.root_group = None
    time.sleep(0.5)

# Exemple d’utilisation
if __name__ == "__main__":
    display = init_display()
    show_demo(display)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nArrêt du programme.")
        sleep_display(display)