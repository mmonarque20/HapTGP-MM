#Code exemple pour tester le fonctionnement de l'écran GC9A01A

import board
import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
from fourwire import FourWire
from vectorio import Circle

from adafruit_gc9a01a import GC9A01A

spi = board.SPI()
tft_cs = board.D8
tft_dc = board.D25
tft_reset = board.D27

displayio.release_displays()

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
display = GC9A01A(display_bus, width=240, height=240)

# Make the display context
main_group = displayio.Group()
display.root_group = main_group

bg_bitmap = displayio.Bitmap(240, 240, 2)
color_palette = displayio.Palette(2)
color_palette[0] = 0xAA00FF  # purple
color_palette[1] = 0xAA0088  # Purple

bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=color_palette, x=0, y=0)
main_group.append(bg_sprite)

#inner_circle = Circle(pixel_shader=color_palette, x=120, y=120, radius=100, color_index=1)


# Cercle avec palette définie directement
inner_circle = Circle(
    pixel_shader=displayio.Palette(1),
    radius=100,
    x=120,
    y=120
)

# Définir la couleur dans la palette
inner_circle.pixel_shader[0] = 0xFFFFFF  # white

main_group.append(inner_circle)

# groupe 1
text_group1 = displayio.Group(scale=2, x=50, y=120)
text1 = "Hello People!"
text_area1 = Label(terminalio.FONT, text=text1, color=0xAA00FF)
text_group1.append(text_area1)  # Subgroup for text scaling
main_group.append(text_group1)

# Groupe 2
text_group2 = displayio.Group(scale=2, x=50, y=150)
text2 = "It's Mary :)"
text_area2 = Label(terminalio.FONT, text=text2, color=0xAA00FF)
text_group2.append(text_area2)
main_group.append(text_group2)

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nArrêt du programme.")

    # Éteindre visuellement l’écran
    black_bitmap = displayio.Bitmap(240, 240, 1)
    black_palette = displayio.Palette(1)
    black_palette[0] = 0x000000
    black_tile = displayio.TileGrid(black_bitmap, pixel_shader=black_palette, x=0, y=0)
    black_group = displayio.Group()
    black_group.append(black_tile)
    display.root_group = black_group
