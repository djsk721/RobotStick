import board
import neopixel
from datetime import datetime
import time

pixels = neopixel.NeoPixel(board.D18,1)
now=datetime.now()
while now.hour>=18:
    pixels.fill((255,0,0))
    pixels.show()
    break
    