#Code exemple pour tester le fonctionnement des dels

import board
import neopixel

pixels = neopixel.NeoPixel(board.D21, 12, pixel_order=neopixel.RGB, auto_write=False)

# Mauve = mélange de rouge et bleu
pixels.fill((0, 50, 50))  # G, R, B

pixels.show()

