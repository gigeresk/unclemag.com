"""Draws the reader's pixel-art Print button (images/printer-*.png) from the Uncle logo.

Three layers the same size, stacked by reader.html: the back of the printer, the paper (which
rises a little on hover), and the front. The printer is drawn on a coarse grid (cells of S
pixels) so it looks chunky; the logo on the paper gets the full resolution so it can be read.

    python3 tools/make_printer.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
S = 2                      # pixels per cell
CW, CH = 48, 44            # canvas, in cells
W, H = CW * S, CH * S

OUT = (110, 74, 36, 255)        # brown outline
CREAM = (251, 233, 192, 255)    # lit top
BODY = (240, 211, 156, 255)     # front face
SHADE = (217, 183, 124, 255)
DARK = (176, 138, 82, 255)
SLOT = (78, 50, 22, 255)
PAPER = (255, 255, 255, 255)
PSHADE = (228, 228, 228, 255)
PLINE = (150, 150, 150, 255)
RED = (200, 36, 44, 255)
RED_D = (142, 26, 31, 255)
RED_L = (226, 80, 80, 255)
GREEN = (40, 150, 70, 255)
GREEN_D = (20, 90, 40, 255)
CLEAR = (0, 0, 0, 0)


def layer():
    return Image.new('RGBA', (W, H), CLEAR)


def rect(im, x0, y0, x1, y1, c):   # in cells, inclusive
    im.paste(c, (x0 * S, y0 * S, (x1 + 1) * S, (y1 + 1) * S))


# ---- paper, top-right corner curled over
paper = layer()
PX0, PX1, PY0, PY1 = 13, 34, 2, 31
rect(paper, PX0, PY0, PX1, PY1, PLINE)
rect(paper, PX0 + 1, PY0 + 1, PX1 - 1, PY1, PAPER)
rect(paper, PX1 - 1, PY0 + 1, PX1 - 1, PY1, PSHADE)
CURL = 5
for i in range(CURL):            # cut the corner off along a diagonal...
    y = PY0 + i
    rect(paper, PX1 - CURL + 1 + i, y, PX1, y, CLEAR)
    rect(paper, PX1 - CURL + 1 + i, y, PX1 - CURL + 1 + i, y, PLINE)
    if i:                        # ...and show the flap folded down under it
        rect(paper, PX1 - CURL + 1, y, PX1 - CURL + i, y, PSHADE)
rect(paper, PX1 - CURL + 1, PY0 + CURL, PX1 - 1, PY0 + CURL, PLINE)
rect(paper, PX1 - CURL, PY0 + 1, PX1 - CURL, PY0 + CURL, PLINE)

# red banner with the logo in white
BY0, BY1 = 10, 21
rect(paper, PX0 + 1, BY0, PX1 - 1, BY1, RED)
rect(paper, PX0 + 1, BY0, PX1 - 1, BY0, RED_L)
rect(paper, PX0 + 1, BY1, PX1 - 1, BY1, RED_D)
logo = Image.open(ROOT / 'images/uncle-logo-black.png').convert('RGBA')
LW = (PX1 - PX0 - 3) * S
LH = round(LW * logo.height / logo.width)
small = logo.resize((LW, LH), Image.LANCZOS)
lx0 = (PX0 + 2) * S - 1
ly0 = (BY0 + 1) * S + ((BY1 - BY0 - 1) * S - LH) // 2
for y in range(LH):
    for x in range(LW):
        if small.getpixel((x, y))[3] > 110:
            paper.putpixel((lx0 + x, ly0 + y), PAPER)
# The slit down the middle of the U is thinner than a pixel at this size, so the U comes out
# solid. Cut it back in, a cell (S pixels) wide so it shows, wherever the full-size logo has
# it (between x 60 and 140).
k = LW / logo.width
for y in range(LH):
    sy = int((y + .5) / k)
    gap = [x for x in range(60, 140) if logo.getpixel((x, sy))[3] < 128]
    if gap and max(gap) - min(gap) < 40:          # the slit, not the open space above the U
        x0 = lx0 + round((min(gap) + max(gap)) / 2 * k - S / 2)
        for dx in range(S):
            paper.putpixel((x0 + dx, ly0 + y), RED)

# ---- printer back: the top deck behind the paper
back = layer()
TX0, TX1, TOP = 6, 41, 25
rect(back, TX0 + 1, TOP, TX1 - 1, TOP, OUT)
rect(back, TX0, TOP + 1, TX0, TOP + 3, OUT)
rect(back, TX1, TOP + 1, TX1, TOP + 3, OUT)
rect(back, TX0 + 1, TOP + 1, TX1 - 1, TOP + 3, CREAM)

# ---- printer front: slot, lip, face with its little slot, buttons and vents
front = layer()
SY = TOP + 3                                  # the slot the paper comes out of
rect(front, TX0, SY, TX0, SY + 3, OUT)
rect(front, TX1, SY, TX1, SY + 3, OUT)
rect(front, TX0 + 1, SY, TX1 - 1, SY + 3, CREAM)
rect(front, PX0 - 2, SY, PX1 + 2, SY + 1, SLOT)
FY0, FY1, FX0, FX1 = SY + 4, CH - 2, TX0 - 1, TX1 + 1   # face, a cell wider than the top
rect(front, FX0, FY0, FX1, FY0, OUT)
rect(front, FX0 + 1, FY1, FX1 - 1, FY1, OUT)
rect(front, FX0, FY0 + 1, FX0, FY1 - 1, OUT)
rect(front, FX1, FY0 + 1, FX1, FY1 - 1, OUT)
rect(front, FX0 + 1, FY0 + 1, FX1 - 1, FY1 - 1, BODY)
rect(front, FX0 + 1, FY0 + 1, FX1 - 1, FY0 + 1, CREAM)   # highlight under the edge
rect(front, FX0 + 1, FY1 - 1, FX1 - 1, FY1 - 1, SHADE)   # shadow along the bottom
rect(front, FX1 - 1, FY0 + 2, FX1 - 1, FY1 - 1, SHADE)
# little paper-feed slot, left
rect(front, FX0 + 4, FY0 + 3, FX0 + 9, FY0 + 3, DARK)
rect(front, FX0 + 4, FY0 + 4, FX0 + 9, FY0 + 4, SHADE)
# buttons, right: red and green
bx = FX1 - 11
rect(front, bx, FY0 + 3, bx + 2, FY0 + 3, RED)
rect(front, bx, FY0 + 4, bx + 2, FY0 + 4, RED_D)
rect(front, bx + 4, FY0 + 3, bx + 6, FY0 + 3, GREEN)
rect(front, bx + 4, FY0 + 4, bx + 6, FY0 + 4, GREEN_D)
# vents
for y in (FY0 + 7, FY0 + 9):
    rect(front, FX0 + 3, y, FX1 - 4, y, SHADE)

for name, im in (('back', back), ('paper', paper), ('front', front)):
    im.save(ROOT / f'images/printer-{name}.png', optimize=True)
print('wrote images/printer-{back,paper,front}.png', (W, H))
