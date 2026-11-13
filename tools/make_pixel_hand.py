"""Pixel-art versions of the hand photos and of the magnifying glass in it, for reader.html:
images/hand-fist-pixel.png, images/hand-open-pixel.png and images/magnifier-pixel.png.

The hand photos are shrunk so that one pixel is one CELL-sized block on screen (at the sizes the
page shows them: see HAND in reader.html), cut down to a few colours and outlined like the printer
and lamp; the wrists fade out with a checkerboard-style dither instead of
see-through pixels.

The glass is drawn rather than shrunk (its rim is too thin to survive): the same shape as the
photo (images/magnifier.png, as reader.html places it: glass radius 100 SVG units round (0,0),
handle out at 45 degrees), on a grid of CELL-sized blocks at the size it is in the hand. The big
glass you pull out stays the photo; only the small one in the hand (or Clippy's) uses
magnifier-pixel.png, saved 8x up so it stays blocky however the SVG it's drawn in scales it.

    python3 tools/make_pixel_hand.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CELL = 3                            # screen pixels per pixel-art pixel (the lamp's size)
HAND = 0.38                         # reader.html: HAND, and OPEN_K = HAND * 0.88
SVG_UNIT = 34 * HAND / 32.7         # reader.html: screen px per glass SVG unit while in the hand
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def pixelate(src, cells_w, colours, edge, fade):
    """fade: the fraction of the way down where the wrist starts fading (dithered below that)."""
    im = Image.open(ROOT / src).convert('RGBA')
    cells_h = round(cells_w * im.height / im.width)
    small = im.resize((cells_w, cells_h), Image.BOX)
    alpha = small.getchannel('A')
    pal = small.convert('RGB').quantize(colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    out = Image.new('RGBA', small.size, (0, 0, 0, 0))
    a, p = alpha.load(), pal.load()
    keep = [[a[x, y] / 255 > ((BAYER[y % 4][x % 4] + .5) / 16 if y > fade * cells_h else .5)
             for x in range(cells_w)] for y in range(cells_h)]
    for y in range(cells_h):
        for x in range(cells_w):
            if keep[y][x]:
                out.putpixel((x, y), p[x, y] + (255,))
    if edge:   # a dark line just outside the shape (and between the fingers), but not round the dithered fade
        for y in range(cells_h):
            for x in range(cells_w):
                if keep[y][x]:
                    continue
                if any(0 <= x + dx < cells_w and 0 <= y + dy <= fade * cells_h and keep[y + dy][x + dx]
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    out.putpixel((x, y), edge)
    return out


fist = pixelate('images/hand-fist.png', round(150 * HAND / CELL), 10, (122, 72, 58, 255), .72)
fist.save(ROOT / 'images/hand-fist-pixel.png', optimize=True)
open_ = pixelate('images/hand-open.png', round(238 * HAND * .88 / CELL), 10, (122, 72, 58, 255), .8)
open_.save(ROOT / 'images/hand-open-pixel.png', optimize=True)

# ---- the glass
N = round(416.3 * SVG_UNIT / CELL)          # cells across the <image> (416.3 SVG units)
U = 416.3 / N                               # SVG units per cell
CX, CY = 143.95 / U, 142.66 / U             # the glass's centre, in cells
RIM = (0x24, 0x24, 0x2a, 255)
RIM_L = (0x70, 0x72, 0x7c, 255)
CHROME = (0xd4, 0xd8, 0xde, 255)
CHROME_D = (0x8c, 0x90, 0x98, 255)
GRIP = (0x1c, 0x1c, 0x22, 255)
GRIP_L = (0x58, 0x5a, 0x64, 255)
GLARE = (255, 255, 255, 200)
glass = Image.new('RGBA', (N, N), (0, 0, 0, 0))
k = 0.70710678
for y in range(N):
    for x in range(N):
        dx, dy = (x + .5 - CX) * U, (y + .5 - CY) * U          # SVG units from the centre
        r = (dx * dx + dy * dy) ** .5
        along, across = (dx + dy) * k, (dy - dx) * k           # along the handle (45 degrees), and across it
        c = None
        if 99 <= r <= 112:                                     # the rim, lit at the top left
            c = RIM_L if dx + dy < -60 and r < 106 else RIM
        elif 92 <= r < 99 and -.95 < (dx + dy) / r / 1.414 < -.55 and dy < 0:
            c = GLARE                                          # a glint inside the top-left of the rim
        elif 108 <= along <= 140 and abs(across) <= 13:        # the chrome neck
            c = CHROME_D if across > 5 else CHROME
        elif 140 < along <= 318 and abs(across) <= 18 or 318 < along and (along - 318) ** 2 + across ** 2 <= 18 ** 2:
            c = GRIP_L if across < -9 else GRIP                # the handle, its top edge catching the light
        if c:
            glass.putpixel((x, y), c)
glass.resize((N * 8, N * 8), Image.NEAREST).save(ROOT / 'images/magnifier-pixel.png', optimize=True)
print('wrote hand-fist-pixel', fist.size, 'hand-open-pixel', open_.size, 'magnifier-pixel', (N, N), 'x8')
