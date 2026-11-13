"""Draws the reader's Back button (images/back-arrow.png): a chunky white double arrow pointing left
(a front arrowhead, and a second chevron behind it), outlined in black with a heavier black shadow
on the bottom right, like an old point-and-click game's. Same pixel art as the rest of the left
margin: one pixel per cell, shown at 3x.

    python3 tools/make_back_arrow.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SW, SH, TIP = 16, 13, 6          # the shape, in cells; the tip's row (the middle)
WHITE = (255, 255, 255, 255)
SHADE = (214, 214, 220, 255)     # the white, along its bottom and right edges
BLACK = (0, 0, 0, 255)


def filled(x, y):
    d = abs(y - TIP)                                   # rows from the tip
    front = d <= x <= 7                                # the front arrowhead, flat-backed
    shaft = d <= 2 and d <= x <= SW - 1                # through the middle to the back
    back = d <= 4 and d + 7 <= x <= SW - 1             # the chevron behind, square at the back
    return front or shaft or back


# shape, then a 1-cell outline, then the shadow (the outline, 1 cell down and right)
P = 1
W, H = SW + 2 * P + 1, SH + 2 * P + 1
shape = {(x + P, y + P) for y in range(SH) for x in range(SW) if filled(x, y)}
outline = {(x + dx, y + dy) for x, y in shape for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - shape
shadow = {(x + 1, y + 1) for x, y in shape | outline} - shape - outline

im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for x, y in shadow | outline:
    im.putpixel((x, y), BLACK)
for x, y in shape:
    edge = (x + 1, y) not in shape or (x, y + 1) not in shape
    im.putpixel((x, y), SHADE if edge else WHITE)
im.save(ROOT / 'images/back-arrow.png', optimize=True)
print('wrote images/back-arrow.png', im.size)
