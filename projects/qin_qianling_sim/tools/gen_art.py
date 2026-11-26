#!/usr/bin/env python3
"""Generate the 2D map, character sprites and UI textures for the Qianling sim.

Everything is drawn procedurally with PIL so the repository carries no
third-party art.  The palette is deliberately muted (earth, rammed earth,
grey tile, dark wood) and every shape gets a shadow so the scene does not
read as flat placeholders.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "assets"
FONT_PATH = "/home/liyutong/.local/share/fonts/noto-cjk/NotoSerifCJKsc-Regular.otf"

W, H = 2880, 1920
random.seed(1898)
np.random.seed(1898)

# palette
EARTH = (176, 154, 118)
EARTH_D = (147, 126, 92)
EARTH_L = (196, 176, 139)
GRASS = (116, 124, 86)
GRASS_D = (96, 105, 71)
ROOF = (86, 84, 78)
ROOF_D = (62, 61, 57)
ROOF_L = (112, 109, 100)
WOOD = (88, 62, 43)
WOOD_D = (60, 41, 28)
WOOD_L = (120, 88, 62)
WALL = (186, 163, 122)
WALL_D = (155, 132, 96)
WALL_L = (207, 186, 146)
STONE = (128, 124, 112)
WATER = (91, 120, 112)
WATER_D = (70, 98, 92)
INK = (48, 40, 32)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    # Noto Serif CJK has no separate bold file in this install; PIL can fake it.
    return ImageFont.truetype(FONT_PATH, size)


def noise_layer(w: int, h: int, amount: float = 10.0) -> Image.Image:
    arr = np.random.normal(0, amount, (h, w, 1)).repeat(3, axis=2)
    return Image.fromarray(np.clip(128 + arr, 0, 255).astype("uint8"))


def add_noise(img: Image.Image, amount: float = 8.0) -> Image.Image:
    n = noise_layer(img.width, img.height, amount)
    return Image.blend(img.convert("RGB"), n, 0.16)


def vgrad(w: int, h: int, top, bottom) -> Image.Image:
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def shadow_rect(img, box, offset=(10, 12), radius=10, alpha=90):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]),
                        radius=radius, fill=(30, 24, 18, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(layer)


def rammed_wall(draw: ImageDraw.ImageDraw, box, thickness=26, horizontal=True):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=WALL)
    # horizontal strata
    step = 9
    for i, y in enumerate(range(y0, y1, step)):
        c = WALL_D if i % 2 else WALL_L
        draw.line([(x0, y), (x1, y)], fill=c, width=2)
    # edge highlight / shadow
    draw.line([(x0, y0), (x1, y0)], fill=(222, 203, 165), width=3)
    draw.line([(x0, y1), (x1, y1)], fill=(120, 101, 74), width=3)
    draw.line([(x1, y0), (x1, y1)], fill=(135, 113, 82), width=3)


def tile_roof(draw, box, ridge=True, eave=True):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=ROOF_D)
    # rows of curved tiles
    row_h = 14
    for j, y in enumerate(range(y0, y1, row_h)):
        draw.rectangle((x0, y, x1, min(y + row_h - 2, y1)), fill=ROOF)
        draw.line([(x0, y + 1), (x1, y + 1)], fill=ROOF_L, width=1)
        # vertical tile divisions, offset each row
        off = 0 if j % 2 == 0 else 9
        for x in range(x0 + off, x1, 18):
            draw.line([(x, y), (x, min(y + row_h - 2, y1))], fill=ROOF_D, width=1)
    if ridge:
        draw.rectangle((x0 - 4, y0 - 5, x1 + 4, y0 + 5), fill=(52, 51, 48))
        draw.line([(x0 - 4, y0 - 4), (x1 + 4, y0 - 4)], fill=(128, 124, 112), width=2)
    if eave:
        draw.rectangle((x0 - 6, y1 - 2, x1 + 6, y1 + 7), fill=(58, 47, 36))
        draw.line([(x0 - 6, y1 + 7), (x1 + 6, y1 + 7)], fill=(38, 31, 24), width=2)


def building(img, box, door_side="south", label=None, roof_box=None):
    """A Qin hall seen from above: tiled roof over most of the footprint,
    a strip of rammed-earth front wall and a timber door at the south edge."""
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    shadow_rect(img, (x0 - 10, y0 - 10, x1 + 10, y1 + 12), offset=(14, 16), radius=6, alpha=100)
    draw = ImageDraw.Draw(img)
    # plinth / terrace
    draw.rectangle((x0 - 10, y0 + 6, x1 + 10, y1 + 12), fill=STONE)
    draw.rectangle((x0 - 10, y0 + 6, x1 + 10, y0 + 14), fill=(154, 149, 134))
    # front wall strip (visible below the roof)
    wall_top = y1 - 52
    draw.rectangle((x0, wall_top, x1, y1 - 8), fill=WALL)
    for y in range(wall_top, y1 - 8, 8):
        draw.line([(x0, y), (x1, y)], fill=WALL_D, width=1)
    for x in range(x0 + 14, x1, 58):
        draw.rectangle((x, wall_top, x + 6, y1 - 8), fill=WOOD_D)
    # door
    dx = (x0 + x1) // 2
    draw.rectangle((dx - 30, y1 - 58, dx + 30, y1 - 8), fill=WOOD_D)
    draw.rectangle((dx - 25, y1 - 54, dx + 25, y1 - 12), fill=(48, 33, 22))
    draw.line([(dx, y1 - 54), (dx, y1 - 12)], fill=(28, 20, 14), width=2)
    for yy in (y1 - 44, y1 - 26):
        draw.ellipse((dx - 14, yy - 3, dx - 8, yy + 3), fill=(150, 120, 60))
        draw.ellipse((dx + 8, yy - 3, dx + 14, yy + 3), fill=(150, 120, 60))
    # roof covers the rest; eave overhangs the front wall
    rx0, ry0, rx1, ry1 = roof_box if roof_box else (x0 - 24, y0 - 22, x1 + 24, y1 - 46)
    shadow_rect(img, (rx0, ry0, rx1, ry1), offset=(16, 18), radius=4, alpha=85)
    draw = ImageDraw.Draw(img)
    tile_roof(draw, (rx0, ry0, rx1, ry1))
    # ridge ornaments at both ends
    for rx in (rx0 + 6, rx1 - 6):
        draw.ellipse((rx - 7, ry0 - 9, rx + 7, ry0 + 5), fill=(52, 51, 48))
    if label:
        f = font(25)
        tw = draw.textlength(label, font=f)
        draw.rounded_rectangle(((x0 + x1) / 2 - tw / 2 - 14, y1 - 2,
                                (x0 + x1) / 2 + tw / 2 + 14, y1 + 30),
                               radius=3, fill=(74, 51, 34), outline=(38, 27, 18), width=2)
        draw.text(((x0 + x1) / 2 - tw / 2, y1 - 1), label, font=f, fill=(222, 203, 165))


def tree(img, x, y, r=42):
    draw = ImageDraw.Draw(img)
    # shadow
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse((x - r * 0.9, y + r * 0.25, x + r * 0.9, y + r * 0.8), fill=(30, 35, 20, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(sh)
    draw = ImageDraw.Draw(img)
    draw.rectangle((x - 5, y - 6, x + 5, y + r * 0.7), fill=(72, 54, 38))
    for (dx, dy, rr, c) in [(-r * 0.45, -r * 0.2, r * 0.62, (83, 96, 60)),
                            (r * 0.42, -r * 0.15, r * 0.58, (74, 88, 55)),
                            (0, -r * 0.55, r * 0.66, (92, 106, 66)),
                            (-r * 0.1, r * 0.05, r * 0.5, (103, 116, 72))]:
        draw.ellipse((x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr), fill=c)
    # leaf specks
    for _ in range(40):
        a = random.random() * math.tau
        rr = random.random() * r * 0.8
        px, py = x + math.cos(a) * rr, y - r * 0.25 + math.sin(a) * rr * 0.7
        draw.point((px, py), fill=(120, 132, 84))


def well(img, x, y):
    draw = ImageDraw.Draw(img)
    shadow_rect(img, (x - 34, y - 26, x + 34, y + 30), offset=(5, 6), radius=10, alpha=70)
    draw = ImageDraw.Draw(img)
    draw.ellipse((x - 34, y - 26, x + 34, y + 30), fill=STONE, outline=(90, 86, 78), width=3)
    draw.ellipse((x - 26, y - 18, x + 26, y + 22), fill=(49, 54, 50))
    draw.arc((x - 26, y - 18, x + 26, y + 22), 200, 340, fill=(110, 120, 112), width=3)


def jar(img, x, y, s=1.0):
    draw = ImageDraw.Draw(img)
    draw.ellipse((x - 14 * s, y + 14 * s, x + 14 * s, y + 22 * s), fill=(40, 32, 24, 80))
    draw.ellipse((x - 14 * s, y - 20 * s, x + 14 * s, y + 18 * s), fill=(96, 74, 53),
                 outline=(60, 44, 30), width=2)
    draw.rectangle((x - 6 * s, y - 24 * s, x + 6 * s, y - 16 * s), fill=(70, 52, 36))


def cart(img, x, y):
    draw = ImageDraw.Draw(img)
    draw.rectangle((x - 42, y - 8, x + 34, y + 16), fill=WOOD, outline=WOOD_D, width=3)
    for wx in (x - 26, x + 22):
        draw.ellipse((wx - 16, y + 10, wx + 16, y + 42), outline=WOOD_D, width=5)
        draw.line([(wx - 12, y + 26), (wx + 12, y + 26)], fill=WOOD_D, width=3)
    draw.line([(x + 30, y + 2), (x + 78, y - 14)], fill=WOOD_D, width=5)


def street(img, box):
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(186, 166, 130))
    # wheel ruts
    for y in range(y0 + 14, y1, 24):
        draw.line([(x0, y), (x1, y)], fill=(170, 150, 116), width=1)
    for x in range(x0, x1, 90):
        draw.line([(x, y0), (x, y1)], fill=(176, 156, 121), width=1)
    # stones
    rnd = random.Random(int(x0 + y0))
    for _ in range((x1 - x0) * (y1 - y0) // 9000):
        px = rnd.uniform(x0, x1)
        py = rnd.uniform(y0, y1)
        r = rnd.uniform(1.5, 4)
        c = (156, 140, 110) if rnd.random() < .5 else (202, 184, 148)
        draw.ellipse((px - r, py - r, px + r, py + r), fill=c)


def river(img, box):
    x0, y0, x1, y1 = box
    g = vgrad(x1 - x0, y1 - y0, (110, 140, 130), (73, 104, 99))
    img.paste(g, (x0, y0))
    draw = ImageDraw.Draw(img)
    for i in range(26):
        yy = y0 + random.uniform(10, y1 - y0 - 10)
        xx = x0 + random.uniform(0, (x1 - x0) * .7)
        ln = random.uniform(40, 180)
        draw.arc((xx, yy, xx + ln, yy + 14), 190, 350, fill=(140, 166, 154), width=2)
    # bank
    draw.rectangle((x0 - 12, y0, x0, y1), fill=(150, 146, 126))
    for y in range(y0, y1, 18):
        draw.ellipse((x0 - 16, y, x0 + 4, y + 12), fill=(128, 124, 108))


def compound(img, box, gate, label, wall_t=24):
    """Walled compound with one gate. gate = ('south'|'north'|'east'|'west', center, width)."""
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(img)
    # courtyard
    draw.rectangle((x0 + wall_t, y0 + wall_t, x1 - wall_t, y1 - wall_t), fill=(190, 170, 133))
    # walls with a gate gap
    side, c, gw = gate
    segs = []
    if side in ("south", "north"):
        y = y1 - wall_t if side == "south" else y0
        segs.append((x0, y, c - gw // 2, y + wall_t))
        segs.append((c + gw // 2, y, x1, y + wall_t))
        segs.append((x0, y0, x0 + wall_t, y1))
        segs.append((x1 - wall_t, y0, x1, y1))
    else:
        x = x1 - wall_t if side == "east" else x0
        segs.append((x, y0, x + wall_t, c - gw // 2))
        segs.append((x, c + gw // 2, x + wall_t, y1))
        segs.append((x0, y0, x1, y0 + wall_t))
        segs.append((x0, y1 - wall_t, x1, y1))
    for s in segs:
        shadow_rect(img, s, offset=(6, 8), radius=2, alpha=55)
        draw = ImageDraw.Draw(img)
        rammed_wall(draw, s, wall_t)
    # gate posts
    if side in ("south", "north"):
        y = y1 - wall_t if side == "south" else y0
        for gx in (c - gw // 2 - 8, c + gw // 2 + 2):
            draw.rectangle((gx, y - 8, gx + 8, y + wall_t + 8), fill=WOOD_D)
            draw.rectangle((gx - 2, y - 14, gx + 10, y - 6), fill=WOOD)
    else:
        x = x1 - wall_t if side == "east" else x0
        for gy in (c - gw // 2 - 8, c + gw // 2 + 2):
            draw.rectangle((x - 8, gy, x + wall_t + 8, gy + 8), fill=WOOD_D)
    # label on a wooden plaque near the gate
    f = font(30)
    tw = draw.textlength(label, font=f)
    if side == "south":
        lx, ly = (c - tw / 2, y1 + 16)
    elif side == "north":
        lx, ly = (c - tw / 2, y0 - 48)
    elif side == "east":
        lx, ly = (x1 + 14, c - 22)
    else:  # west
        lx, ly = (x0 - tw - 14, c - 22)
    draw.rounded_rectangle((lx - 14, ly - 6, lx + tw + 14, ly + 38), radius=3,
                           fill=(78, 55, 37), outline=(42, 30, 20), width=2)
    draw.text((lx, ly), label, font=f, fill=(224, 206, 168))


def draw_map() -> tuple[Image.Image, dict]:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # ground
    ground = Image.new("RGB", (W, H), EARTH)
    gd = ImageDraw.Draw(ground)
    rnd = random.Random(7)
    for _ in range(260):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(40, 190)
        gd.ellipse((x - r, y - r * .6, x + r, y + r * .6),
                   fill=(GRASS if rnd.random() < .55 else EARTH_L))
    ground = ground.filter(ImageFilter.GaussianBlur(22))
    ground = add_noise(ground, 9)
    img.paste(ground, (0, 0))

    # river on the east
    river(img, (2700, 40, W, H - 40))
    # outer rammed wall
    draw = ImageDraw.Draw(img)
    for seg in [(40, 40, W - 250, 80), (40, H - 80, W - 250, H - 40),
                (40, 40, 80, H - 40), (W - 290, 40, W - 250, H - 40)]:
        shadow_rect(img, seg, offset=(8, 10), radius=2, alpha=70)
        draw = ImageDraw.Draw(img)
        rammed_wall(draw, seg, 40)
    # city gates: south and east
    for (gx0, gy0, gx1, gy1) in [(1360, H - 90, 1500, H - 30), (W - 300, 900, W - 240, 1040)]:
        draw.rectangle((gx0, gy0, gx1, gy1), fill=(70, 52, 36))
        draw.rectangle((gx0 + 8, gy0 + 8, gx1 - 8, gy1 - 8), fill=(48, 35, 24))

    # streets
    street(img, (80, 930, W - 250, 1050))       # east-west
    street(img, (1360, 80, 1480, H - 80))       # north-south
    street(img, (80, 700, 1360, 760))           # to county office / granary
    street(img, (1480, 700, W - 250, 760))
    street(img, (80, 1450, 1360, 1510))
    street(img, (1480, 1450, W - 250, 1510))

    # compounds
    compound(img, (160, 150, 1040, 780), ("south", 600, 110), "县廷")
    compound(img, (1700, 150, 2520, 780), ("west", 470, 110), "仓")
    compound(img, (160, 1120, 1040, 1740), ("east", 1400, 110), "都乡")
    compound(img, (1700, 1120, 2520, 1740), ("north", 2110, 110), "邮亭")

    # buildings
    building(img, (250, 235, 760, 520), "south", "大堂")
    building(img, (810, 260, 970, 520), "south", "曹")
    building(img, (1800, 220, 2110, 500), "south", "仓廪")
    building(img, (2170, 220, 2460, 500), "south", "仓廪")
    building(img, (230, 1180, 640, 1430), "south", "乡部")
    building(img, (790, 1200, 960, 1380), "south", "里门")
    building(img, (1800, 1180, 2130, 1430), "south", "亭舍")
    building(img, (2200, 1200, 2440, 1400), "south", "厩")

    # courtyard details
    well(img, 880, 640)
    well(img, 2050, 640)
    well(img, 880, 1580)
    well(img, 2050, 1580)
    for (x, y) in [(300, 600), (330, 660), (660, 620), (700, 690)]:
        jar(img, x, y)
    for (x, y) in [(1860, 610), (1900, 650), (2360, 620), (2400, 660)]:
        jar(img, x, y, .9)
    cart(img, 560, 860)
    cart(img, 1120, 1600)
    cart(img, 1600, 700)
    # haystacks near granary
    for (x, y, r) in [(2260, 620, 34), (2320, 640, 30)]:
        draw = ImageDraw.Draw(img)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(158, 134, 82))
        draw.arc((x - r, y - r, x + r, y + r), 200, 340, fill=(120, 99, 60), width=3)

    # trees along streets and in courtyards
    for (x, y, r) in [(120, 860, 34), (1240, 860, 32), (1540, 860, 34), (2580, 860, 30),
                      (120, 1080, 32), (1240, 1080, 34), (1540, 1080, 32), (2580, 1080, 30),
                      (120, 1600, 30), (1240, 1600, 32), (1540, 1600, 34), (2580, 1600, 30),
                      (1120, 300, 36), (1120, 600, 32), (1100, 1250, 32), (1120, 1650, 30),
                      (1620, 300, 30), (1620, 600, 32), (1620, 1250, 32), (1620, 1650, 30)]:
        tree(img, x, y, r)

    # subtle vignette
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse((-W * .15, -H * .2, W * 1.15, H * 1.2), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(180))
    black = Image.new("RGBA", (W, H), (20, 16, 12, 150))
    img = Image.composite(img, black, vig)

    # collision rectangles (walkable blockers)
    blockers = []
    # outer walls
    blockers += [[40, 40, W - 250, 80], [40, H - 80, W - 250, H - 40],
                 [40, 40, 80, H - 40], [W - 290, 40, W - 250, H - 40]]
    # compound walls (approximate, with gaps)
    blockers += [
        [160, 150, 545, 174], [655, 150, 1040, 174], [160, 150, 184, 780], [1016, 150, 1040, 780],
        [160, 756, 545, 780], [655, 756, 1040, 780],
        [1700, 150, 2520, 174], [1700, 150, 1724, 415], [1700, 525, 1724, 780],
        [1700, 756, 2520, 780],
        [160, 1120, 1040, 1144], [160, 1120, 184, 1740], [1016, 1120, 1040, 1345], [1016, 1455, 1040, 1740],
        [160, 1716, 1040, 1740],
        [1700, 1120, 2055, 1144], [2165, 1120, 2520, 1144], [1700, 1120, 1724, 1740],
        [2496, 1120, 2520, 1740], [1700, 1716, 2520, 1740],
    ]
    # buildings
    blockers += [
        [250, 235, 760, 520], [810, 260, 970, 520],
        [1800, 220, 2110, 500], [2170, 220, 2460, 500],
        [230, 1180, 640, 1430], [790, 1200, 960, 1380],
        [1800, 1180, 2130, 1430], [2200, 1200, 2440, 1400],
    ]
    # water
    blockers.append([2690, 40, W, H - 40])
    # canvas edges (the south gate otherwise walks into the void)
    blockers += [[0, 1880, W, 1920], [0, 0, W, 20], [0, 0, 20, H], [W - 20, 0, W, H]]
    # trees (trunk only, so player can walk under canopy)
    for (x, y, r) in [(120, 860, 34), (1240, 860, 32), (1540, 860, 34), (2580, 860, 30),
                      (120, 1080, 32), (1240, 1080, 34), (1540, 1080, 32), (2580, 1080, 30),
                      (120, 1600, 30), (1240, 1600, 32), (1540, 1600, 34), (2580, 1600, 30),
                      (1120, 300, 36), (1120, 600, 32), (1100, 1250, 32), (1120, 1650, 30),
                      (1620, 300, 30), (1620, 600, 32), (1620, 1250, 32), (1620, 1650, 30)]:
        blockers.append([x - 8, y + 4, x + 8, y + 18])
    # carts / wells roughly
    for (x, y) in [(560, 860), (1120, 1600), (1600, 700), (880, 640), (2050, 640), (880, 1580), (2050, 1580)]:
        blockers.append([x - 26, y - 16, x + 26, y + 26])

    meta = {
        "size": [W, H],
        "blockers": blockers,
        "spawn": [620, 710],
        "locations": {
            "county": [600, 680],
            "granary": [2050, 640],
            "township": [600, 1500],
            "post": [2110, 1550],
        },
        "npcs": {
            "cheng": [480, 670],
            "xiang": [430, 1480],
            "lidian": [760, 1620],
            "cang": [1880, 600],
            "you": [2000, 1570],
            "wife": [520, 1600],
        },
        "objects": {
            "death_report": [800, 680],
            "law_shelf": [990, 650],
            "body": [2000, 680],
            "wound": [2150, 680],
            "grain_ledger": [2300, 700],
            "register": [650, 1520],
            "post_slip": [2300, 1500],
        },
    }
    return img, meta


def character(name: str, robe, accent, hat="cap", direction="down", frame=0):
    """48x64 character sprite, four directions, two walk frames."""
    im = Image.new("RGBA", (48, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # shadow
    d.ellipse((10, 56, 38, 63), fill=(20, 18, 14, 90))
    # legs
    off = 2 if frame else -2
    d.rectangle((18, 44, 22, 57 + off), fill=(48, 42, 36))
    d.rectangle((26, 44, 30, 57 - off), fill=(48, 42, 36))
    # robe
    d.polygon([(14, 24), (34, 24), (37, 48), (11, 48)], fill=robe, outline=(38, 30, 24))
    # sleeves
    d.polygon([(14, 26), (6, 38), (12, 42), (17, 34)], fill=robe, outline=(38, 30, 24))
    d.polygon([(34, 26), (42, 38), (36, 42), (31, 34)], fill=robe, outline=(38, 30, 24))
    # belt
    d.rectangle((14, 36, 34, 40), fill=accent)
    # collar
    d.line([(20, 24), (24, 32), (28, 24)], fill=(226, 214, 186), width=2)
    # head
    d.ellipse((17, 8, 31, 24), fill=(206, 176, 138), outline=(70, 52, 38))
    # hair / hat
    if hat == "cap":
        d.rectangle((16, 6, 32, 12), fill=(34, 32, 30))
        d.rectangle((14, 10, 34, 13), fill=(28, 26, 24))
    elif hat == "tall":
        d.rectangle((15, 2, 33, 8), fill=(34, 32, 30))
        d.rectangle((18, -4, 30, 3), fill=(34, 32, 30))
    elif hat == "cloth":
        d.rectangle((16, 5, 32, 11), fill=(96, 82, 62))
    elif hat == "woman":
        d.rectangle((15, 5, 17, 19), fill=(38, 32, 28))
        d.rectangle((31, 5, 33, 19), fill=(38, 32, 28))
        d.ellipse((27, 0, 36, 9), fill=(38, 32, 28))
        d.rectangle((17, 4, 31, 9), fill=(38, 32, 28))
    else:
        d.ellipse((16, 4, 32, 12), fill=(40, 36, 32))
    # face direction
    if direction == "down":
        d.ellipse((20, 15, 22, 17), fill=INK)
        d.ellipse((26, 15, 28, 17), fill=INK)
        d.line([(22, 21), (26, 21)], fill=(120, 82, 64))
    elif direction == "left":
        d.ellipse((18, 15, 20, 17), fill=INK)
        d.line([(17, 20), (21, 20)], fill=(120, 82, 64))
    elif direction == "right":
        d.ellipse((28, 15, 30, 17), fill=INK)
        d.line([(27, 20), (31, 20)], fill=(120, 82, 64))
    else:  # up
        d.rectangle((17, 8, 31, 14), fill=(34, 32, 30))
    # outline pass for readability
    return im


def ui_textures():
    # bamboo-slip document panel background
    w, h = 900, 640
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w - 6, h - 6), radius=8, fill=(214, 193, 151),
                        outline=(92, 68, 44), width=4)
    # vertical bamboo slips
    for x in range(18, w - 18, 30):
        d.rectangle((x, 18, x + 24, h - 18), fill=(196, 170, 120), outline=(160, 134, 90), width=1)
        d.line([(x + 2, 18), (x + 2, h - 18)], fill=(222, 200, 158), width=2)
        d.line([(x + 22, 18), (x + 22, h - 18)], fill=(168, 143, 100), width=1)
    # binding cords
    for y in (60, 320, 580):
        d.line([(10, y), (w - 10, y)], fill=(110, 80, 52), width=3)
    im.save(OUT / "ui" / "slips_panel.png")

    # seal stamp
    s = 120
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, s - 4, s - 4), radius=6, fill=(150, 46, 38))
    d.rounded_rectangle((12, 12, s - 12, s - 12), radius=3, outline=(224, 190, 160), width=3)
    d.text((22, 24), "遷陵", font=font(30), fill=(232, 208, 180))
    d.text((22, 62), "丞印", font=font(30), fill=(232, 208, 180))
    im.save(OUT / "ui" / "seal.png")

    # interaction marker
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, 28, 28), fill=(226, 206, 160, 230), outline=(80, 58, 38), width=2)
    d.text((10, 5), "E", font=font(16), fill=(60, 44, 30))
    im.save(OUT / "ui" / "prompt.png")


def main():
    (OUT / "tiles").mkdir(parents=True, exist_ok=True)
    (OUT / "sprites").mkdir(parents=True, exist_ok=True)
    (OUT / "ui").mkdir(parents=True, exist_ok=True)
    (ROOT / "artifacts").mkdir(parents=True, exist_ok=True)
    img, meta = draw_map()
    img.convert("RGB").save(OUT / "tiles" / "map_base.png")
    img.convert("RGB").resize((1440, 960), Image.LANCZOS).save(ROOT / "artifacts" / "map_preview.png")
    (ROOT / "game" / "data" / "map_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    cast = {
        "player": ((62, 78, 92), (176, 146, 92), "cap"),
        "cheng": ((96, 54, 50), (176, 146, 92), "tall"),
        "xiang": ((104, 84, 58), (150, 122, 78), "cap"),
        "lidian": ((88, 88, 72), (132, 112, 80), "cloth"),
        "cang": ((120, 94, 52), (166, 134, 80), "cap"),
        "you": ((70, 88, 74), (120, 116, 84), "cloth"),
        "wife": ((74, 70, 86), (132, 108, 96), "woman"),
    }
    for name, (robe, accent, hat) in cast.items():
        for direction in ("down", "up", "left", "right"):
            for frame in (0, 1):
                character(name, robe, accent, hat, direction, frame).save(
                    OUT / "sprites" / f"{name}_{direction}_{frame}.png")
    ui_textures()
    object_icons()
    print("map + sprites written")



def object_icons():
    out = OUT / "sprites"
    # bundle of bamboo slips
    im = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((6, 36, 38, 42), fill=(20, 18, 14, 80))
    for i, x in enumerate(range(8, 36, 6)):
        d.rectangle((x, 6, x + 5, 38), fill=(190, 164, 112), outline=(110, 82, 52))
    d.line([(6, 14), (38, 14)], fill=(90, 62, 40), width=2)
    d.line([(6, 30), (38, 30)], fill=(90, 62, 40), width=2)
    im.save(out / "obj_slips.png")

    # ledger board
    im = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 36, 40, 42), fill=(20, 18, 14, 80))
    d.rectangle((5, 5, 39, 38), fill=(126, 92, 60), outline=(64, 44, 28), width=2)
    d.rectangle((8, 8, 36, 34), fill=(196, 170, 120))
    for y in range(12, 33, 6):
        d.line([(11, y), (33, y)], fill=(96, 70, 46), width=1)
    im.save(out / "obj_ledger.png")

    # law bundle
    im = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 36, 40, 42), fill=(20, 18, 14, 80))
    d.rounded_rectangle((7, 8, 37, 36), radius=4, fill=(200, 176, 128), outline=(96, 70, 44), width=2)
    d.ellipse((7, 4, 37, 18), fill=(210, 186, 138), outline=(96, 70, 44), width=2)
    d.line([(12, 22), (32, 22)], fill=(90, 64, 42), width=2)
    d.line([(12, 28), (28, 28)], fill=(90, 64, 42), width=2)
    im.save(out / "obj_law.png")

    # seal box / clay
    im = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 36, 40, 42), fill=(20, 18, 14, 80))
    d.rounded_rectangle((7, 14, 37, 38), radius=3, fill=(120, 78, 54), outline=(64, 42, 28), width=2)
    d.rectangle((11, 18, 33, 34), fill=(150, 48, 40))
    d.rectangle((15, 22, 29, 30), outline=(226, 198, 170), width=1)
    d.line([(16, 17), (28, 17)], fill=(210, 186, 138), width=3)
    im.save(out / "obj_seal.png")

    # covered body on a mat (no gore)
    im = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((5, 26, 39, 40), radius=3, fill=(170, 148, 108))
    d.ellipse((8, 12, 36, 34), fill=(118, 104, 86), outline=(62, 50, 38), width=2)
    d.line([(12, 18), (32, 30)], fill=(86, 74, 60), width=2)
    d.ellipse((31, 10, 37, 16), fill=(150, 132, 104))
    im.save(out / "obj_body.png")

    # grain sack with a blood stain
    im = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 38, 40, 43), fill=(20, 18, 14, 80))
    d.rounded_rectangle((8, 10, 36, 38), radius=8, fill=(176, 150, 100), outline=(96, 74, 46), width=2)
    d.rectangle((13, 6, 31, 12), fill=(120, 96, 62))
    d.ellipse((24, 24, 32, 32), fill=(112, 38, 32))
    d.ellipse((20, 28, 26, 34), fill=(132, 44, 36))
    im.save(out / "obj_wound.png")


if __name__ == "__main__":
    main()
