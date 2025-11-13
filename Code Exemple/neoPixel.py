import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D21, 12, pixel_order=neopixel.RGB, auto_write=False)

try:
    # Allume les DELs en mauve
    pixels.fill((0, 50, 50))  # G, R, B
    pixels.show()

    # Laisse allumé pendant 5 secondes
    time.sleep(5)

except KeyboardInterrupt:
    print("Arrêt manuel du programme.")

finally:
    # Éteint les DELs proprement
    pixels.fill((0, 0, 0))
    pixels.show()
    print("DELs éteintes.")