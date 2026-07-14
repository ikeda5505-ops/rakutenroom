# -*- coding: utf-8 -*-
"""The Quiet Shelf — Rakuten ROOM brand: icon + header."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

CREAM   = (247, 243, 236)
SAGE    = (143, 169, 143)
SAGE_D  = (110, 138, 110)
TERRA   = (201, 123, 90)
INK     = (62, 74, 61)
LINEN   = (236, 229, 217)

SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SANS  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SANS_B= "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def grain(img, amount=5, seed=7):
    random.seed(seed)
    px = img.load()
    w, h = img.size
    step = 3
    for y in range(0, h, step):
        for x in range(0, w, step):
            n = random.randint(-amount, amount)
            r, g, b = px[x, y][:3]
            px[x, y] = (max(0,min(255,r+n)), max(0,min(255,g+n)), max(0,min(255,b+n)))
    return img

def spaced(draw, xy, text, font, fill, tracking=0, anchor_center_x=None):
    """Draw text with letter tracking. If anchor_center_x given, center the block."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text)-1)
    x, y = xy
    if anchor_center_x is not None:
        x = anchor_center_x - total/2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total

# ------------------------------------------------------------------ ICON
S = 1080
SS = 4  # supersample
W = S*SS
im = Image.new("RGB", (W, W), CREAM)
d = ImageDraw.Draw(im)

cx = W/2
# outer thin ring
ring_r = int(W*0.455)
d.ellipse([cx-ring_r, cx-ring_r, cx+ring_r, cx+ring_r], outline=SAGE, width=int(W*0.006))
# inner linen circle
disc_r = int(W*0.415)
d.ellipse([cx-disc_r, cx-disc_r, cx+disc_r, cx+disc_r], fill=LINEN)

# sun arc rising behind the shelf (terracotta half-disc)
sun_r = int(W*0.16)
sun_cy = int(W*0.435)
d.pieslice([cx-sun_r, sun_cy-sun_r, cx+sun_r, sun_cy+sun_r], 180, 360, fill=TERRA)

# shelf line
shelf_y = sun_cy
shelf_half = int(W*0.26)
d.line([cx-shelf_half, shelf_y, cx+shelf_half, shelf_y], fill=INK, width=int(W*0.008))

# small vessel (left) and plant stem (right) resting on the shelf
v_w, v_h = int(W*0.052), int(W*0.055)
vx = cx - shelf_half + int(W*0.052)
d.rounded_rectangle([vx-v_w/2, shelf_y-v_h, vx+v_w/2, shelf_y-int(W*0.004)],
                    radius=int(W*0.012), fill=SAGE_D)
px_ = cx + shelf_half - int(W*0.055)
stem_top = shelf_y - int(W*0.085)
d.line([px_, shelf_y-int(W*0.004), px_, stem_top], fill=SAGE_D, width=int(W*0.0075))
leaf = int(W*0.030)
d.ellipse([px_-leaf-int(W*0.006), stem_top-int(leaf*0.7), px_-int(W*0.006), stem_top+int(leaf*0.55)], fill=SAGE)
d.ellipse([px_+int(W*0.006), stem_top-leaf, px_+leaf+int(W*0.006), stem_top+int(leaf*0.25)], fill=SAGE)

# monumental character 暮
f_big = ImageFont.truetype(SERIF, int(W*0.30), index=2)  # JP face
bbox = d.textbbox((0,0), "暮", font=f_big)
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
ty = int(W*0.455)
d.text((cx - tw/2 - bbox[0], ty), "暮", font=f_big, fill=INK)

# name, letter-spaced beneath
f_name = ImageFont.truetype(SANS, int(W*0.048))
spaced(d, (0, int(W*0.800)), "くらし研究室", f_name, INK, tracking=int(W*0.020), anchor_center_x=cx)
f_sub = ImageFont.truetype(SANS, int(W*0.024))
spaced(d, (0, int(W*0.866)), "ラクする名品だけ", f_sub, SAGE_D, tracking=int(W*0.013), anchor_center_x=cx)

im = im.resize((S, S), Image.LANCZOS)
im = grain(im, 4)
im.save("/home/claude/room_icon.png")

# ---------------------------------------------------------------- HEADER
HW, HH = 1500, 500
SS = 3
W2, H2 = HW*SS, HH*SS
hd = Image.new("RGB", (W2, H2), CREAM)
d = ImageDraw.Draw(hd)

# right-side composition: sun, arcs, plant, vessel — a quiet shelf scene
rx = int(W2*0.795)
base_y = int(H2*0.72)

# large sage circle backdrop (plate) — fully contained between keylines
plate_r = int(H2*0.335)
plate_cy = int(H2*0.475)
d.ellipse([rx-plate_r, plate_cy-plate_r, rx+plate_r, plate_cy+plate_r],
          outline=SAGE, width=int(H2*0.010))

# terracotta sun half-disc on the shelf line
sun_r = int(H2*0.20)
d.pieslice([rx-sun_r, base_y-sun_r, rx+sun_r, base_y+sun_r], 180, 360, fill=TERRA)

# shelf line across right zone
d.line([int(W2*0.60), base_y, int(W2*0.965), base_y], fill=INK, width=int(H2*0.014))

# vessel left of sun
vx = int(W2*0.645); v_w, v_h = int(H2*0.085), int(H2*0.09)
d.rounded_rectangle([vx-v_w/2, base_y-v_h, vx+v_w/2, base_y-int(H2*0.006)],
                    radius=int(H2*0.02), fill=SAGE_D)
# steam arcs above vessel
for i, off in enumerate((-1, 1)):
    ar = int(H2*0.045) + i*int(H2*0.02)
    d.arc([vx-ar, base_y-v_h-int(H2*0.10)-ar, vx+ar, base_y-v_h-int(H2*0.10)+ar],
          200, 340, fill=SAGE, width=int(H2*0.008))

# plant right of sun
px_ = int(W2*0.935)
stem_top = base_y - int(H2*0.16)
d.line([px_, base_y-int(H2*0.006), px_, stem_top], fill=SAGE_D, width=int(H2*0.010))
leaf = int(H2*0.055)
d.ellipse([px_-leaf-8, stem_top-int(leaf*0.7), px_-8, stem_top+int(leaf*0.55)], fill=SAGE)
d.ellipse([px_+8, stem_top-leaf, px_+leaf+8, stem_top+int(leaf*0.25)], fill=SAGE)

# thin frame keylines top/bottom
d.line([int(W2*0.035), int(H2*0.10), int(W2*0.965), int(H2*0.10)], fill=SAGE, width=int(H2*0.006))
d.line([int(W2*0.035), int(H2*0.90), int(W2*0.965), int(H2*0.90)], fill=SAGE, width=int(H2*0.006))

# left text block
f_h1 = ImageFont.truetype(SANS_B, int(H2*0.155))
tx = int(W2*0.055)
spaced(d, (tx, int(H2*0.24)), "くらし研究室", f_h1, INK, tracking=int(H2*0.030))
f_h2 = ImageFont.truetype(SANS, int(H2*0.062))
spaced(d, (tx+int(H2*0.008), int(H2*0.48)), "暮らしがラクになる名品だけを、厳選。", f_h2, SAGE_D, tracking=int(H2*0.012))

# small credential line with terracotta dot markers
f_h3 = ImageFont.truetype(SANS, int(H2*0.050))
y3 = int(H2*0.655)
dot_r = int(H2*0.016)
x3 = tx + int(H2*0.010)
for label in ("レビュー500件以上", "★4.3以上", "毎日更新"):
    d.ellipse([x3, y3+int(H2*0.022), x3+dot_r*2, y3+int(H2*0.022)+dot_r*2], fill=TERRA)
    x3 += dot_r*2 + int(H2*0.025)
    wlab = spaced(d, (x3, y3), label, f_h3, INK, tracking=int(H2*0.006))
    x3 += wlab + int(H2*0.06)

hd = hd.resize((HW, HH), Image.LANCZOS)
hd = grain(hd, 4, seed=11)
hd.save("/home/claude/room_header.png")
print("done")
