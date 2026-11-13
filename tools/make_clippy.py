"""Clippy for the reader: a trimmed copy of the clippy.js sprite sheet and animation data.

clippy.js (github.com/smore-inc/clippy.js, MIT) ships Clippy as one big sheet of 124x93 frames
(agents/Clippy/map.png, 1.3MB) and the animations as clippy.ready('Clippy', {...}) in
agents/Clippy/agent.js. The reader only uses a handful of animations, so this keeps just their
frames, packs them into a small sheet, and rewrites the animations to point at it:

   images/clippy.png    the frames, ROW_LEN to a row with a GAP of see-through pixels between
                        them (so a frame scaled up smoothly doesn't pick up an edge of the next),
                        in the original palette
   images/clippy.json   {"framesize": [w, h], "pitch": [w + GAP, h + GAP], "cols": ROW_LEN,
                        "animations": {name: [frame, ...]}}
                        where a frame is [duration ms, sheet index or -1 (blank), exitBranch or -1,
                        [[frameIndex, weight], ...]] (the clippy.js branching, sounds left out)

Usage: python3 tools/make_clippy.py path/to/map.png path/to/agent.js
"""
import json
import sys
from pathlib import Path

from PIL import Image

KEEP = [
    'RestPose', 'Show',
    # idle fidgets, now and then
    'IdleEyeBrowRaise', 'IdleHeadScratch', 'IdleFingerTap', 'IdleSideToSide',
    'LookRight', 'LookUpRight', 'LookDownRight',
    # talking to you
    'Greeting', 'Hearing_1', 'Thinking', 'Explain', 'GestureRight', 'GestureLeft',
    'GetAttention', 'Alert',
]
ROW_LEN = 16
GAP = 2

ROOT = Path(__file__).resolve().parent.parent


def main(map_path, agent_path):
    text = Path(agent_path).read_text()
    data = json.loads(text[text.index('{'):text.rindex('}') + 1])   # data only, never run
    fw, fh = data['framesize']
    sheet = Image.open(map_path)   # a palette image, one index see-through: kept as it is
    if sheet.mode != 'P':
        raise SystemExit('expected a palette PNG')

    index = {}   # (x, y) in the old sheet -> index in the new one
    anims = {}
    for name in KEEP:
        frames = []
        for f in data['animations'][name]['frames']:
            imgs = f.get('images') or []
            if len(imgs) > 1:
                raise SystemExit(f'{name}: overlay frames not supported')
            i = -1
            if imgs:
                i = index.setdefault(tuple(imgs[0]), len(index))
            branches = [[b['frameIndex'], b['weight']] for b in (f.get('branching') or {}).get('branches', [])]
            frames.append([f['duration'], i, f.get('exitBranch', -1), branches])
        anims[name] = frames

    n = len(index)
    rows = (n + ROW_LEN - 1) // ROW_LEN
    clear = sheet.info['transparency']
    pw, ph = fw + GAP, fh + GAP
    out = Image.new('P', (ROW_LEN * pw - GAP, rows * ph - GAP), clear)
    out.putpalette(sheet.getpalette())
    for (x, y), i in index.items():
        out.paste(sheet.crop((x, y, x + fw, y + fh)), ((i % ROW_LEN) * pw, (i // ROW_LEN) * ph))
    out.save(ROOT / 'images/clippy.png', optimize=True, transparency=clear)

    (ROOT / 'images/clippy.json').write_text(json.dumps(
        {'framesize': [fw, fh], 'pitch': [pw, ph], 'cols': ROW_LEN, 'animations': anims}, separators=(',', ':')))
    print(f'{n} frames, {rows} rows, {(ROOT / "images/clippy.png").stat().st_size // 1024}KB png, '
          f'{(ROOT / "images/clippy.json").stat().st_size // 1024}KB json')


if __name__ == '__main__':
    main(*sys.argv[1:3])
