"""Draws the reader's desk lamp (images/lamp-off.png, images/lamp-on.png), in the same chunky
pixel art as the printer (tools/make_printer.py): a red anglepoise lamp, base at the bottom left,
chrome arms up to a shade that points down and to the right, at the magazine. "On" lights the
inside of the shade and the bulb. Hovered, it turns to look at you: halfway round
(lamp-mid-off/-on.png), then the shade seen end-on (lamp-look-off/-on.png).

One pixel per cell; reader.html shows it at 3x.
The lamp's light is drawn by the page, from the middle of the shade's mouth, at cell MOUTH below.

    python3 tools/make_lamp.py
"""
from math import cos, sin, radians, hypot
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
W, H = 37, 40

OUT = (58, 20, 22, 255)          # outline
RED = (211, 33, 45, 255)         # the crayon red
RED_L = (238, 92, 92, 255)
RED_D = (142, 26, 31, 255)
STEEL = (196, 200, 208, 255)
STEEL_L = (240, 242, 246, 255)
STEEL_D = (120, 126, 136, 255)
JOINT = (70, 70, 78, 255)
INSIDE_OFF = (64, 30, 32, 255)    # the inside of the shade, unlit
INSIDE_ON = (255, 236, 160, 255)  # ...and lit
BULB_OFF = (214, 214, 200, 255)
BULB_ON = (255, 252, 230, 255)
GLOW = (255, 214, 110, 255)
CLEAR = (0, 0, 0, 0)

AXIS = radians(38)                 # the shade points down-right at this angle below level
APEX = (21.5, 7.5)                 # back of the shade (where it hangs off the arm)
LENGTH, BACK_R, MOUTH_R = 10.5, 2.6, 6.2


def along(p, d, a=AXIS):
    return (p[0] + d * cos(a), p[1] + d * sin(a))


def side(p, d, a=AXIS):           # d cells to the side of the axis (positive: up-right of it)
    return (p[0] + d * sin(a), p[1] - d * cos(a))


MOUTH = along(APEX, LENGTH)


def part(draw_fn):
    """A mask (mode L) of one part, drawn by draw_fn(ImageDraw)."""
    m = Image.new('L', (W, H), 0)
    draw_fn(ImageDraw.Draw(m))
    return m


def shade_part(im, mask, base, lit, dark):
    """Fill mask with base, lit along its top/left edges and dark along its bottom/right ones."""
    px = mask.load()
    for y in range(H):
        for x in range(W):
            if not px[x, y]:
                continue
            up = y == 0 or not px[x, y - 1]
            left = x == 0 or not px[x - 1, y]
            down = y == H - 1 or not px[x, y + 1]
            right = x == W - 1 or not px[x + 1, y]
            c = lit if (up or left) and not (down or right) else dark if (down or right) and not (up or left) else base
            im.putpixel((x, y), c)


def outline(im):
    """A one-cell outline round everything drawn so far (4-neighbours)."""
    src = im.copy()
    a = src.load()
    for y in range(H):
        for x in range(W):
            if a[x, y][3]:
                continue
            if any(0 <= x + dx < W and 0 <= y + dy < H and a[x + dx, y + dy][3] and a[x + dx, y + dy] != OUT
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                im.putpixel((x, y), OUT)


FACE = (26.5, 9.5)                 # looking at you: the middle of the shade's round face


def ellipse(c, a, b, ang):
    """Points round an ellipse at c: a across the axis at angle ang, b along it."""
    pts = []
    for k in range(48):
        t = 2 * 3.14159265 * k / 48
        x, y = a * cos(t), b * sin(t)          # x across the axis, y along it
        pts.append((c[0] + y * cos(ang) + x * sin(ang), c[1] + y * sin(ang) - x * cos(ang)))
    return pts


def lamp(on, look=False):
    """look: True for the shade turned to face you (on hover), its round mouth and the bulb in
    it; 'mid' for halfway round, the mouth an oval."""
    im = Image.new('RGBA', (W, H), CLEAR)
    # arms first (behind the joints and shade): base -> elbow -> head
    base_top, elbow, head = (8, 33), (5.5, 16), APEX
    arms = part(lambda d: (d.line([base_top, elbow], fill=255, width=2), d.line([elbow, head], fill=255, width=2)))
    shade_part(im, arms, STEEL, STEEL_L, STEEL_D)
    # a spring alongside the lower arm
    for k in range(4):
        x, y = 7.6 + (5.5 - 8) * (k + 1) / 6, 33 + (16 - 33) * (k + 1) / 6
        im.putpixel((round(x + 1.5), round(y)), STEEL_D)
    # base: a low dome
    base = part(lambda d: (d.rectangle([2, 35, 14, 37], fill=255), d.rectangle([4, 33, 12, 34], fill=255),
                           d.rectangle([6, 32, 10, 32], fill=255)))
    shade_part(im, base, RED, RED_L, RED_D)
    # joints
    for c, r in ((elbow, 1.6), (head, 1.4)):
        jm = part(lambda d, c=c, r=r: d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255))
        shade_part(im, jm, JOINT, STEEL_D, JOINT)
    if look == 'mid':
        return three_quarter(im, on)
    if look:
        return face(im, on)
    # the shade: a cone from the rounded back to the mouth
    back_up, back_dn = side(APEX, BACK_R), side(APEX, -BACK_R)
    mouth_up, mouth_dn = side(MOUTH, MOUTH_R), side(MOUTH, -MOUTH_R)
    cap = along(APEX, -1.6)
    sh = part(lambda d: (d.polygon([back_up, mouth_up, mouth_dn, back_dn], fill=255),
                         d.ellipse([cap[0] - BACK_R, cap[1] - BACK_R, cap[0] + BACK_R, cap[1] + BACK_R], fill=255)))
    shade_part(im, sh, RED, RED_L, RED_D)
    # the mouth, seen edge-on: a thin band across the end of the cone, lit or not, and the bulb
    # just showing past it
    rim = part(lambda d: d.line([side(along(MOUTH, -.6), MOUTH_R - .6), side(along(MOUTH, -.6), -MOUTH_R + .6)],
                                fill=255, width=2))
    bulb_c = along(MOUTH, -.4)
    bulb = part(lambda d: d.ellipse([bulb_c[0] - 2.3, bulb_c[1] - 2.3, bulb_c[0] + 2.3, bulb_c[1] + 2.3], fill=255))
    rp, bp = rim.load(), bulb.load()
    for y in range(H):
        for x in range(W):
            if rp[x, y]:
                im.putpixel((x, y), INSIDE_ON if on else INSIDE_OFF)
    for y in range(H):
        for x in range(W):
            # only the half of the bulb beyond the mouth
            if bp[x, y] and (x + .5 - MOUTH[0]) * cos(AXIS) + (y + .5 - MOUTH[1]) * sin(AXIS) > -.9:
                im.putpixel((x, y), BULB_ON if on else BULB_OFF)
    outline(im)
    if on:   # a warm ring of glow round the bulb's outline
        a = im.load()
        for y in range(H):
            for x in range(W):
                if not a[x, y][3] and hypot(x + .5 - bulb_c[0], y + .5 - bulb_c[1]) < 4.3:
                    im.putpixel((x, y), GLOW)
    return im


def face(im, on):
    """The shade seen end-on: a red ring, the inside of the shade, the bulb in the middle."""
    def disc(r):
        return part(lambda d: d.ellipse([FACE[0] - r, FACE[1] - r, FACE[0] + r, FACE[1] + r], fill=255))
    shade_part(im, disc(MOUTH_R + .3), RED, RED_L, RED_D)
    inner, bulb = disc(MOUTH_R - 1.4), disc(2.6)
    ip, bp = inner.load(), bulb.load()
    for y in range(H):
        for x in range(W):
            if bp[x, y]:
                im.putpixel((x, y), BULB_ON if on else BULB_OFF)
            elif ip[x, y]:
                # the inside of the shade, a little darker toward the bottom right
                dark = (x + .5 - FACE[0]) + (y + .5 - FACE[1]) > 2.5
                c = INSIDE_ON if on else INSIDE_OFF
                im.putpixel((x, y), tuple(int(v * .8) for v in c[:3]) + (255,) if dark else c)
    im.putpixel((int(FACE[0] - 1.2), int(FACE[1] - 1.2)), (255, 255, 255, 255))   # a glint on the bulb
    outline(im)
    if on:   # a warm ring of glow round the face
        a = im.load()
        for y in range(H):
            for x in range(W):
                if not a[x, y][3] and hypot(x + .5 - FACE[0], y + .5 - FACE[1]) < MOUTH_R + 2.6:
                    im.putpixel((x, y), GLOW)
    return im


def three_quarter(im, on):
    """Halfway between side-on and facing you: a shorter cone, its mouth an oval you can see into."""
    turn = .6                                  # how much of the cone's length still shows
    mc = along(APEX, LENGTH * turn)            # the mouth's middle
    ra, rb = MOUTH_R, MOUTH_R * .72            # the mouth: full width across, squashed along the axis
    def poly(pts):
        return part(lambda d: d.polygon(pts, fill=255))
    back_up, back_dn = side(APEX, BACK_R), side(APEX, -BACK_R)
    cap = along(APEX, -1.6)
    cone = part(lambda d: (d.polygon([back_up, side(mc, ra), side(mc, -ra), back_dn], fill=255),
                           d.ellipse([cap[0] - BACK_R, cap[1] - BACK_R, cap[0] + BACK_R, cap[1] + BACK_R], fill=255),
                           d.polygon(ellipse(mc, ra + .3, rb + .3, AXIS), fill=255)))
    shade_part(im, cone, RED, RED_L, RED_D)
    inner, bulb = poly(ellipse(mc, ra - 1.3, rb - 1.1, AXIS)), poly(ellipse(along(mc, -.3), 2.5, 2.0, AXIS))
    ip, bp = inner.load(), bulb.load()
    for y in range(H):
        for x in range(W):
            if bp[x, y]:
                im.putpixel((x, y), BULB_ON if on else BULB_OFF)
            elif ip[x, y]:
                im.putpixel((x, y), INSIDE_ON if on else INSIDE_OFF)
    outline(im)
    if on:
        a = im.load()
        for y in range(H):
            for x in range(W):
                if not a[x, y][3] and hypot(x + .5 - mc[0], y + .5 - mc[1]) < ra + 2.3:
                    im.putpixel((x, y), GLOW)
    return im


for name, on, look in (('off', False, False), ('on', True, False), ('mid-off', False, 'mid'), ('mid-on', True, 'mid'),
                       ('look-off', False, True), ('look-on', True, True)):
    lamp(on, look).save(ROOT / f'images/lamp-{name}.png', optimize=True)
print('wrote images/lamp-{off,on,mid-off,mid-on,look-off,look-on}.png', (W, H), 'mouth at', tuple(round(v, 2) for v in MOUTH),
      'face at', FACE)
