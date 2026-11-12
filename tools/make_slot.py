"""Draws the round grey button the crayons and pencil lie on (images/slot.png), in the same
chunky pixel art as the printer (tools/make_printer.py), but finer: a 76-cell disc with a raised rim lit
from the top left and a sunken well in the middle, like the inventory slots of 90s CD-ROM games.
One pixel per cell; reader.html shows it at 2x on computers (half the printer's cell size), as
wide as the printer's body.

    python3 tools/make_slot.py
"""
from math import hypot
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
N = 76                     # diameter, in cells
C = N / 2

OUT = (46, 46, 50, 255)         # outline
HI = (246, 246, 246, 255)       # rim, lit
RIM_L = (214, 214, 218, 255)
RIM = (178, 178, 184, 255)
RIM_D = (128, 128, 134, 255)
LO = (92, 92, 98, 255)          # rim, in shadow
WELL_D = (104, 104, 110, 255)   # the well's edge in shadow (top left: it's sunken)
WELL_L = (206, 206, 210, 255)   # ...and lit (bottom right)
FACE = (160, 160, 166, 255)
CLEAR = (0, 0, 0, 0)

R_OUT, R_RIM, R_WELL, EDGE = 38.0, 36.6, 27.2, 2.2   # outline | rim | well edge (EDGE wide) | face


def light(dx, dy):
    """How much this edge faces the light (top left): 1 facing it, -1 facing away."""
    d = hypot(dx, dy) or 1
    return (-dx - dy) / d / 2 ** 0.5


im = Image.new('RGBA', (N, N), CLEAR)
for y in range(N):
    for x in range(N):
        dx, dy = x + .5 - C, y + .5 - C
        d = hypot(dx, dy)
        if d > R_OUT:
            continue
        L = light(dx, dy)
        if d > R_RIM:
            c = OUT
        elif d > R_WELL + EDGE:          # raised rim: bright top left, dark bottom right
            c = HI if L > .6 else RIM_L if L > .15 else RIM if L > -.3 else RIM_D if L > -.7 else LO
        elif d > R_WELL:              # sunken well's edge: the other way round
            c = WELL_D if L > .2 else FACE if L > -.2 else WELL_L
        else:
            c = FACE
        im.putpixel((x, y), c)
im.save(ROOT / 'images/slot.png')
print('images/slot.png', im.size)
