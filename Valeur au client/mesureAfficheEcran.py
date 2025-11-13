import board
import time
import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
from fourwire import FourWire
from vectorio import Circle
import bme280
import veml7700
from adafruit_gc9a01a import GC9A01A

# Initialisation SPI et écran
spi = board.SPI()
tft_cs = board.D8
tft_dc = board.D25
tft_reset = board.D27

displayio.release_displays()
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
display = GC9A01A(display_bus, width=240, height=240)

# Groupe principal
main_group = displayio.Group()
display.root_group = main_group

# Fond violet
bg_bitmap = displayio.Bitmap(240, 240, 2)
color_palette = displayio.Palette(2)
color_palette[0] = 0xAA00FF  # violet
color_palette[1] = 0xAA0088  # violet foncé
bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=color_palette, x=0, y=0)
main_group.append(bg_sprite)

# Cercle blanc au centre
inner_circle = Circle(pixel_shader=displayio.Palette(1), radius=100, x=120, y=120)
inner_circle.pixel_shader[0] = 0xFFFFFF  # blanc
main_group.append(inner_circle)

# Groupe de texte
text_group = displayio.Group(scale=2, x=30, y=30)
main_group.append(text_group)

# Création des labels (vides au départ)
label_temp = Label(terminalio.FONT, text="", color=0xAA00FF, x=25, y=10)
label_hum = Label(terminalio.FONT, text="", color=0xAA00FF, x=25, y=20)
label_pres = Label(terminalio.FONT, text="", color=0xAA00FF, x=25, y=30)
label_alt = Label(terminalio.FONT, text="", color=0xAA00FF, x=25, y=40)
label_lux = Label(terminalio.FONT, text="", color=0xAA00FF, x=25, y=50)

# Ajout des labels au groupe
text_group.append(label_temp)
text_group.append(label_hum)
text_group.append(label_pres)
text_group.append(label_alt)
text_group.append(label_lux)

# Boucle principale avec mise à jour toutes les 5 secondes
try:
    while True:
        # Effacer les textes
        label_temp.text = ""
        label_hum.text = ""
        label_pres.text = ""
        label_alt.text = ""
        label_lux.text = ""

        # Attendre un court instant pour que l'effacement soit visible
        time.sleep(0.1)

        # Mettre à jour les textes avec les nouvelles données
        label_temp.text = f"{bme280.getTemperature():.1f} °C"
        label_hum.text = f"{bme280.getHumidity():.1f} %"
        label_pres.text = f"{bme280.getPressure():.1f} hPa"
        label_alt.text = f"{bme280.getAltitude():.1f} m"
        label_lux.text = f"{veml7700.getLuminosite():.1f} lux"

        time.sleep(5)

except KeyboardInterrupt:
    print("\nArrêt du programme.")
    # Éteindre visuellement l’écran
    display.root_group = None
    time.sleep(0.5)
