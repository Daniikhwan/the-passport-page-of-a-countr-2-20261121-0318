#!/usr/bin/env python3
"""
The Passport Page of a Country That Isn't There
make.fun competition: the-passport-page-of-a-countr-2-20261121-0318

Entry program: draws one invented passport spread (1024x1024 PNG) to
/output/entry.png using only the Python standard library, so it runs in
the grading sandbox with no network and no third-party packages.

The invented country is the Republic of Kestria, a windswept North
Atlantic island republic (capital Havnestad). The holder is Eirik Magnus
Haldorsson, a seaman of the fishing vessel MV Skarven. Every date on the
spread is internally consistent: the passport was issued 02 JUN 2021 and
expires 01 JUN 2031; every stamp falls between those dates, and the MRZ
check digits follow ICAO Doc 9303.
"""

import math
import os
import random
import struct
import zlib

# ---------------------------------------------------------------- font 5x7
# Each glyph is 7 rows of 5 characters ('#' = ink, '.' = empty).
# Uppercase + digits + common punctuation; passports are set in capitals.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", "..#..", "..#.."),
    ',': (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '/': ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    ':': (".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
}


def text_width(s, scale=1, spacing=1):
    """Width in pixels of string s rendered at the given scale."""
    if not s:
        return 0
    return len(s) * (5 * scale + spacing) - spacing


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg=(255, 255, 255)):
        self.w = w
        self.h = h
        self.clip = None  # (x0, y0, x1, y1) or None
        self.px = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            return (self.px[i], self.px[i + 1], self.px[i + 2])
        return (255, 255, 255)

    def blend(self, x, y, color, alpha):
        """Alpha-blend color over the pixel (alpha 0..1)."""
        if not (0 <= x < self.w and 0 <= y < self.h) or alpha <= 0:
            return
        if self.clip is not None:
            cx0, cy0, cx1, cy1 = self.clip
            if not (cx0 <= x < cx1 and cy0 <= y < cy1):
                return
        if alpha >= 1:
            self.set(x, y, color)
            return
        i = self._idx(x, y)
        r0, g0, b0 = self.px[i], self.px[i + 1], self.px[i + 2]
        r1, g1, b1 = color
        self.px[i] = int(r0 + (r1 - r0) * alpha)
        self.px[i + 1] = int(g0 + (g1 - g0) * alpha)
        self.px[i + 2] = int(b0 + (b1 - b0) * alpha)

    def fill_rect(self, x, y, w, h, color, alpha=1.0):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        if alpha >= 1.0:
            row = bytes(color) * (x1 - x0)
            for yy in range(y0, y1):
                i = self._idx(x0, yy)
                self.px[i:i + len(row)] = row
            return
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                self.blend(xx, yy, color, alpha)

    def rect(self, x, y, w, h, color, t=1, alpha=1.0):
        self.fill_rect(x, y, w, t, color, alpha)
        self.fill_rect(x, y + h - t, w, t, color, alpha)
        self.fill_rect(x, y, t, h, color, alpha)
        self.fill_rect(x + w - t, y, t, h, color, alpha)

    def line(self, x0, y0, x1, y1, color, t=1, alpha=1.0):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = int(round(x0 + dx * i / steps))
            y = int(round(y0 + dy * i / steps))
            if t <= 1:
                self.blend(x, y, color, alpha)
            else:
                r = t // 2
                self.fill_rect(x - r, y - r, t, t, color, alpha)

    def circle(self, cx, cy, r, color, t=1, alpha=1.0, fill=False):
        if fill:
            for yy in range(cy - r, cy + r + 1):
                for xx in range(cx - r, cx + r + 1):
                    if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                        self.blend(xx, yy, color, alpha)
            return
        steps = max(8, int(2 * math.pi * r))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            x = int(round(cx + r * math.cos(a)))
            y = int(round(cy + r * math.sin(a)))
            if t <= 1:
                self.blend(x, y, color, alpha)
            else:
                rr = t // 2
                self.fill_rect(x - rr, y - rr, t, t, color, alpha)

    def ellipse(self, cx, cy, rx, ry, color, t=1, alpha=1.0, fill=False):
        if fill:
            for yy in range(cy - ry, cy + ry + 1):
                for xx in range(cx - rx, cx + rx + 1):
                    if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1:
                        self.blend(xx, yy, color, alpha)
            return
        steps = max(16, int(2 * math.pi * max(rx, ry)))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            x = int(round(cx + rx * math.cos(a)))
            y = int(round(cy + ry * math.sin(a)))
            if t <= 1:
                self.blend(x, y, color, alpha)
            else:
                rr = t // 2
                self.fill_rect(x - rr, y - rr, t, t, color, alpha)

    def polygon(self, pts, color, alpha=1.0):
        """Scanline-filled polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(max(0, int(math.ceil(xs[j]))),
                               min(self.w, int(math.floor(xs[j + 1])) + 1)):
                    self.blend(x, y, color, alpha)

    def text(self, x, y, s, color, scale=1, spacing=1, alpha=1.0,
             align="left", shear=0.0):
        """Draw text with the 5x7 font. shear shifts rows right as y grows
        (fake italic). Returns the drawn width in pixels."""
        s = s.upper()
        w = text_width(s, scale, spacing)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                shift = int(round(shear * row * scale))
                for col in range(5):
                    if glyph[row][col] == '#':
                        self.fill_rect(cx + col * scale + shift,
                                       y + row * scale, scale, scale,
                                       color, alpha)
            cx += 5 * scale + spacing
        return w

    def blit_rotated(self, src, cx, cy, angle_deg, alpha=1.0):
        """Blit src canvas rotated by angle_deg around (cx, cy).
        Pixels exactly the paper colour are transparent."""
        ang = math.radians(angle_deg)
        ca, sa = math.cos(ang), math.sin(ang)
        sw, sh = src.w, src.h
        # bounding box of rotated src
        corners = [(-sw / 2, -sh / 2), (sw / 2, -sh / 2),
                   (sw / 2, sh / 2), (-sw / 2, sh / 2)]
        rot = [(x * ca - y * sa, x * sa + y * ca) for x, y in corners]
        xs = [p[0] for p in rot]
        ys = [p[1] for p in rot]
        x0, x1 = int(cx + min(xs)), int(cx + max(xs))
        y0, y1 = int(cy + min(ys)), int(cy + max(ys))
        for yy in range(max(0, y0), min(self.h, y1 + 1)):
            for xx in range(max(0, x0), min(self.w, x1 + 1)):
                dx, dy = xx - cx, yy - cy
                sx = dx * ca + dy * sa + sw / 2
                sy = -dx * sa + dy * ca + sh / 2
                ix, iy = int(sx), int(sy)
                if 0 <= ix < sw and 0 <= iy < sh:
                    c = src.get(ix, iy)
                    if c != PAPER:
                        self.blend(xx, yy, c, alpha)


def write_png(canvas, path):
    """Write an RGB PNG with the Up filter (stdlib only). The image is
    mostly flat colour, so Up compresses nearly as well as per-row filter
    selection at a fraction of the runtime."""
    w, h = canvas.w, canvas.h
    raw = bytearray()
    prev = bytearray(w * 3)
    for y in range(h):
        row = canvas.px[y * w * 3:(y + 1) * w * 3]
        f = bytearray(len(row))
        for i in range(len(row)):
            f[i] = (row[i] - prev[i]) & 0xFF
        raw.append(2)
        raw.extend(f)
        prev = bytearray(row)
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)

# ---------------------------------------------------------------------- MRZ
# ICAO Doc 9303 check digits: value map A=10..Z=35, '<'=0, digits as-is;
# weights cycle 7, 3, 1; check digit = sum mod 10.
_MRZ_VAL = {}
for _i, _ch in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    _MRZ_VAL[_ch] = _i if _i < 10 else _i - 10 + 10
_MRZ_VAL['<'] = 0


def mrz_check(s):
    total = 0
    for i, ch in enumerate(s):
        total += _MRZ_VAL[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    """Two 44-character MRZ lines for the Kestrian passport, with correct
    check digits (verified by construction, not hard-coded)."""
    name = "HALDORSSON<<EIRIK<MAGNUS"
    line1 = ("P<KES" + name).ljust(44, "<")
    doc = "KST004821"
    doc_cd = mrz_check(doc)
    nat = "KES"
    dob = "870314"
    dob_cd = mrz_check(dob)
    sex = "M"
    exp = "310601"
    exp_cd = mrz_check(exp)
    personal = "<" * 14
    personal_cd = mrz_check(personal)
    composite = doc + doc_cd + nat + dob + dob_cd + sex + exp + exp_cd + personal + personal_cd
    comp_cd = mrz_check(composite)
    line2 = doc + doc_cd + nat + dob + dob_cd + sex + exp + exp_cd + personal + personal_cd + comp_cd
    assert len(line1) == 44 and len(line2) == 44
    return line1, line2


# ------------------------------------------------------------- paper & ink
PAPER = (244, 239, 226)      # warm passport paper
PAPER_DARK = (232, 225, 206)
INK = (26, 42, 74)           # deep navy document ink
INK_SOFT = (58, 74, 110)
RED = (158, 44, 34)          # burgundy seal red
GOLD = (146, 108, 42)
STAMP_BLUE = (43, 76, 155)
STAMP_RED = (168, 51, 39)
STAMP_PURPLE = (107, 63, 160)
STAMP_GREEN = (46, 110, 72)


def guilloche(c, x, y, w, h, color, alpha=0.5):
    """Fine wavy security lines across a page area."""
    for k in range(0, h, 5):
        yy = y + k
        for xx in range(x, x + w, 2):
            off = int(2.2 * math.sin((xx - x) * 0.045 + k * 0.35))
            c.blend(xx, yy + off, color, alpha)


def paper_speckle(c, x, y, w, h, rng, n=900):
    for _ in range(n):
        xx = rng.randint(x, x + w - 1)
        yy = rng.randint(y, y + h - 1)
        v = rng.randint(0, 2)
        col = (228, 222, 200) if v == 0 else ((250, 246, 236) if v == 1 else (222, 214, 190))
        c.set(xx, yy, col)


def draw_shadow(c, x, y, w, h, blur=10):
    for i in range(blur, 0, -1):
        a = 0.05 + 0.10 * (blur - i) / blur
        c.fill_rect(x + i, y + i, w, h, (10, 12, 18), a * 0.35)


# ------------------------------------------------------------------ portrait
def draw_portrait(c, x, y, w, h, rng):
    """Stylised passport photograph: a weathered North Atlantic seaman in
    his late thirties, woollen cap, dark jacket. Drawn as layered shapes
    with dithered shading so it reads as a photograph at stamp size."""
    # photo background: pale studio grey-blue with a soft vignette
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            t = (yy - y) / h
            base = (178 + int(14 * t), 186 + int(12 * t), 196 + int(10 * t))
            dx = (xx - (x + w / 2)) / (w / 2)
            dy = (yy - (y + h / 2)) / (h / 2)
            d = min(1.0, math.sqrt(dx * dx + dy * dy))
            shade = 1.0 - 0.16 * max(0.0, d - 0.55) / 0.45
            c.set(xx, yy, (int(base[0] * shade), int(base[1] * shade),
                           int(base[2] * shade)))
    cx = x + w // 2
    # shoulders / jacket
    c.polygon([(x + 8, y + h), (x + w - 8, y + h),
               (x + w - 6, y + int(h * 0.86)), (cx + 34, y + int(h * 0.80)),
               (cx + 26, y + int(h * 0.72)), (cx - 26, y + int(h * 0.72)),
               (cx - 34, y + int(h * 0.80)), (x + 6, y + int(h * 0.86))],
              (52, 58, 72))
    # shirt + collar
    c.polygon([(cx - 22, y + int(h * 0.74)), (cx + 22, y + int(h * 0.74)),
               (cx + 12, y + int(h * 0.86)), (cx - 12, y + int(h * 0.86))],
              (228, 226, 218))
    c.polygon([(cx - 22, y + int(h * 0.74)), (cx, y + int(h * 0.82)),
               (cx - 12, y + int(h * 0.86)), (cx - 22, y + int(h * 0.80))],
              (198, 196, 188))
    c.polygon([(cx + 22, y + int(h * 0.74)), (cx, y + int(h * 0.82)),
               (cx + 12, y + int(h * 0.86)), (cx + 22, y + int(h * 0.80))],
              (198, 196, 188))
    # neck
    c.fill_rect(cx - 15, y + int(h * 0.62), 30, int(h * 0.13), (196, 152, 118))
    c.fill_rect(cx - 15, y + int(h * 0.62), 30, 5, (168, 126, 96))
    # head: weathered skin, slightly wide jaw
    hx, hy = cx, y + int(h * 0.36)
    c.ellipse(hx, hy, 40, 48, (206, 164, 128), fill=True)
    # jaw shading
    c.ellipse(hx, hy + 22, 30, 22, (196, 152, 116), fill=True)
    # ears
    c.ellipse(hx - 38, hy + 4, 5, 10, (198, 156, 120), fill=True)
    c.ellipse(hx + 38, hy + 4, 5, 10, (198, 156, 120), fill=True)
    # hair: dark, receding at the temples, swept back
    c.polygon([(hx - 40, hy - 8), (hx - 38, hy - 42), (hx - 20, hy - 52),
               (hx + 6, hy - 54), (hx + 30, hy - 48), (hx + 40, hy - 30),
               (hx + 40, hy - 8), (hx + 30, hy - 26), (hx + 8, hy - 34),
               (hx - 18, hy - 32), (hx - 32, hy - 22)], (58, 44, 34))
    # forehead lines
    c.line(hx - 24, hy - 26, hx + 22, hy - 28, (178, 138, 104), 1, 0.6)
    # eyebrows: heavy, straight
    c.fill_rect(hx - 26, hy - 12, 20, 4, (62, 48, 36))
    c.fill_rect(hx + 7, hy - 12, 20, 4, (62, 48, 36))
    # eyes
    for ex in (hx - 16, hx + 16):
        c.ellipse(ex, hy - 2, 8, 5, (238, 234, 226), fill=True)
        c.circle(ex, hy - 2, 4, (74, 96, 110), fill=True)
        c.circle(ex, hy - 2, 2, (28, 24, 20), fill=True)
        c.line(ex - 8, hy - 6, ex + 8, hy - 6, (90, 70, 52), 1)
    # nose: shadow + nostrils
    c.line(hx + 2, hy + 2, hx + 3, hy + 20, (172, 132, 100), 2, 0.8)
    c.line(hx - 4, hy + 20, hx + 9, hy + 20, (160, 120, 90), 2, 0.8)
    c.circle(hx - 3, hy + 21, 1, (120, 88, 64), fill=True)
    c.circle(hx + 8, hy + 21, 1, (120, 88, 64), fill=True)
    # cheek shading
    c.ellipse(hx - 24, hy + 14, 10, 7, (196, 150, 114), fill=True, alpha=0.5)
    c.ellipse(hx + 24, hy + 14, 10, 7, (196, 150, 114), fill=True, alpha=0.5)
    # mouth: closed, straight, faint smile lines
    c.line(hx - 12, hy + 32, hx + 12, hy + 32, (146, 104, 78), 2)
    c.line(hx - 14, hy + 30, hx - 12, hy + 32, (160, 120, 92), 1, 0.7)
    c.line(hx + 14, hy + 30, hx + 12, hy + 32, (160, 120, 92), 1, 0.7)
    # stubble on jaw
    for _ in range(260):
        sx = rng.randint(hx - 30, hx + 30)
        sy = rng.randint(hy + 26, hy + 46)
        if ((sx - hx) / 34) ** 2 + ((sy - (hy + 30)) / 22) ** 2 <= 1:
            c.blend(sx, sy, (120, 96, 72), 0.35)
    # photo grain
    for _ in range(500):
        gx = rng.randint(x, x + w - 1)
        gy = rng.randint(y, y + h - 1)
        c.blend(gx, gy, (255, 255, 255) if rng.random() < 0.5 else (0, 0, 0),
                0.05)

def draw_portrait_small(c, x, y, w, h, rng):
    """The same seaman at stamp size: a few shapes, clipped to the box."""
    old_clip = c.clip
    c.clip = (x, y, x + w, y + h)
    for yy in range(y, y + h):
        t = (yy - y) / h
        base = (178 + int(14 * t), 186 + int(12 * t), 196 + int(10 * t))
        c.fill_rect(x, yy, w, 1, base)
    cx = x + w // 2
    c.polygon([(x + 2, y + h), (x + w - 2, y + h), (cx + 12, y + int(h * 0.78)),
               (cx - 12, y + int(h * 0.78))], (52, 58, 72))
    c.fill_rect(cx - 6, y + int(h * 0.60), 12, int(h * 0.18), (196, 152, 118))
    hx, hy = cx, y + int(h * 0.36)
    c.ellipse(hx, hy, 13, 15, (206, 164, 128), fill=True)
    c.polygon([(hx - 13, hy - 2), (hx - 12, hy - 13), (hx - 4, hy - 16),
               (hx + 5, hy - 16), (hx + 12, hy - 13), (hx + 13, hy - 2),
               (hx + 8, hy - 9), (hx - 8, hy - 9)], (58, 44, 34))
    c.fill_rect(hx - 9, hy - 4, 7, 2, (62, 48, 36))
    c.fill_rect(hx + 2, hy - 4, 7, 2, (62, 48, 36))
    for ex in (hx - 5, hx + 5):
        c.circle(ex, hy + 1, 2, (238, 234, 226), fill=True)
        c.circle(ex, hy + 1, 1, (28, 24, 20), fill=True)
    c.line(hx + 1, hy + 3, hx + 1, hy + 8, (172, 132, 100), 1, 0.8)
    c.line(hx - 4, hy + 11, hx + 4, hy + 11, (146, 104, 78), 1)
    c.clip = old_clip


# ------------------------------------------------------------------ emblem
def draw_emblem(c, cx, cy, r, color=GOLD):
    """Kestrian arms: a tern in flight above three waves, inside a ring."""
    c.circle(cx, cy, r, color, 2)
    c.circle(cx, cy, r - 4, color, 1)
    # waves
    for k, wy in enumerate((cy + r // 3, cy + r // 2 + 2, cy + 2 * r // 3)):
        amp = 4 + k
        for xx in range(cx - r + 6, cx + r - 5):
            yy = wy + int(amp * math.sin((xx - cx) * 0.16))
            c.blend(xx, yy, color, 0.9)
    # tern: two swept wings + body
    c.polygon([(cx - r + 8, cy - 2), (cx - 4, cy - r + 10), (cx, cy - 4)],
              color)
    c.polygon([(cx + r - 8, cy - 2), (cx + 4, cy - r + 10), (cx, cy - 4)],
              color)
    c.line(cx - 2, cy - 4, cx + 8, cy - 2, color, 2)
    # stars
    for sx, sy in ((cx - r + 12, cy - r + 12), (cx + r - 12, cy - r + 12)):
        c.fill_rect(sx - 1, sy - 3, 3, 7, color)
        c.fill_rect(sx - 3, sy - 1, 7, 3, color)


def draw_signature(c, x, y, w, color=INK):
    """A quick ink signature: E. Haldorsson, as a polyline squiggle."""
    pts = [(0, 14), (6, 2), (10, 16), (16, 4), (20, 14), (26, 6),
           (30, 14), (38, 8), (44, 14), (52, 4), (58, 12), (66, 6),
           (72, 14), (80, 8), (88, 14)]
    sx = x
    sy = y
    for i in range(len(pts) - 1):
        c.line(sx + pts[i][0], sy + pts[i][1],
               sx + pts[i + 1][0], sy + pts[i + 1][1], color, 2)
    c.line(x + w - 26, y + 16, x + w - 2, y + 16, color, 1)


# ------------------------------------------------------------------ stamps
def rect_stamp(lines, w, h, color, scale=1, border=3, dashed=False):
    """A rectangular ink stamp on its own paper-coloured canvas (for
    rotation); the paper colour blits as transparent."""
    cv = Canvas(w, h, PAPER)
    cv.rect(2, 2, w - 4, h - 4, color, border)
    if dashed:
        cv.rect(7, 7, w - 14, h - 14, color, 1)
    total = sum(7 * sc + 4 for _, sc in lines) - 4
    y = (h - total) // 2
    for txt, sc in lines:
        tw = text_width(txt, sc, 1)
        cv.text((w - tw) // 2, y, txt, color, sc, 1)
        y += 7 * sc + 4
    return cv


def circle_stamp(top, mid, bottom, r, color, scale=1):
    """A circular date stamp with straight text lines inside."""
    d = 2 * r + 8
    cv = Canvas(d, d, PAPER)
    cx = cy = d // 2
    cv.circle(cx, cy, r, color, 3)
    cv.circle(cx, cy, r - 5, color, 1)
    # small stars left/right of the middle line
    for sx in (cx - r + 12, cx + r - 12):
        cv.fill_rect(sx - 1, cy - 3, 3, 7, color)
        cv.fill_rect(sx - 3, cy - 1, 7, 3, color)
    cv.text(cx, cy - 7 * scale - 16, top, color, scale, 1, align="center")
    cv.text(cx, cy - 4, mid, color, scale, 1, align="center")
    cv.text(cx, cy + 12, bottom, color, scale, 1, align="center")
    return cv


def visa_sticker(c, x, y, w, h):
    """Schengen-style visa sticker: green/blue gradient bands, photo box,
    fields and a machine-readable strip at the bottom."""
    # pale sticker body with a two-tone band
    c.fill_rect(x, y, w, h, (214, 226, 214))
    for yy in range(y, y + h):
        t = (yy - y) / h
        col = (196 + int(30 * t), 214, 196 + int(18 * t))
        c.fill_rect(x, yy, w, 1, col)
    c.rect(x, y, w, h, (46, 110, 72), 2)
    c.fill_rect(x, y, w, 20, (46, 110, 72))
    c.text(x + 8, y + 5, "SCHENGEN VISA", (255, 255, 255), 1, 1)
    c.text(x + w - 8, y + 5, "C", (255, 255, 255), 1, 1, align="right")
    # mini photo box (same seaman, small)
    rng = random.Random(7)
    draw_portrait_small(c, x + 10, y + 30, 52, 64, rng)
    c.rect(x + 10, y + 30, 52, 64, INK, 1)
    # fields
    fx = x + 72
    rows = [("SURNAME", "HALDORSSON"),
            ("GIVEN NAMES", "EIRIK MAGNUS"),
            ("VALID", "01 MAR 2024 - 28 FEB 2025"),
            ("ENTRIES", "MULTIPLE   STAY 90 DAYS"),
            ("ISSUED", "OSLO  12 FEB 2024")]
    yy = y + 30
    for label, val in rows:
        c.text(fx, yy, label, (90, 96, 110), 1, 1)
        c.text(fx, yy + 9, val, INK, 1, 1)
        yy += 20
    # visa number + MRZ-ish strip
    c.text(x + 10, y + h - 26, "NOR 004821  90  01", INK, 1, 1)
    c.text(x + 10, y + h - 14, "V<NORHALDORSSON<<EIRIK<MAGNUS<<<<", INK, 1, 1)

# -------------------------------------------------------------- page build
def field(c, x, y, label, value):
    c.text(x, y, label, INK_SOFT, 1, 1)
    c.text(x, y + 9, value, INK, 2, 1)


def bold_text(c, x, y, s, color, scale=1, spacing=1, align="left"):
    w = text_width(s, scale, spacing)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    c.text(x, y, s, color, scale, spacing)
    c.text(x + 1, y, s, color, scale, spacing)
    return w


def build_data_page(c, px, py, pw, ph, rng):
    c.fill_rect(px, py, pw, ph, PAPER)
    guilloche(c, px + 12, py + 12, pw - 24, ph - 24, (120, 150, 190), 0.35)
    paper_speckle(c, px, py, pw, ph, rng, 500)
    c.rect(px, py, pw, ph, INK, 2)
    c.rect(px + 6, py + 6, pw - 12, ph - 12, INK_SOFT, 1, 0.7)
    # header: arms + country name
    draw_emblem(c, px + pw // 2, py + 54, 24)
    bold_text(c, px + pw // 2, py + 86, "REPUBLIC OF KESTRIA", INK, 2, 1,
              align="center")
    c.text(px + pw // 2, py + 108, "PASSPORT  -  VEGABREF", INK_SOFT, 1, 1,
           align="center")
    c.line(px + 30, py + 126, px + pw - 30, py + 126, INK, 1)
    # type / code / number
    ty = py + 140
    c.text(px + 30, ty, "TYPE", INK_SOFT, 1, 1)
    c.text(px + 66, ty, "P", INK, 2, 1)
    c.text(px + 130, ty, "CODE", INK_SOFT, 1, 1)
    c.text(px + 168, ty, "KES", INK, 2, 1)
    c.text(px + 236, ty, "PASSPORT NO.", INK_SOFT, 1, 1)
    c.text(px + 322, ty, "KST 004821", INK, 2, 1)
    # portrait
    phx, phy, phw, phh = px + 30, py + 168, 150, 190
    draw_portrait(c, phx, phy, phw, phh, rng)
    c.rect(phx, phy, phw, phh, INK, 2)
    # fields beside the portrait
    fx = px + 200
    fy = py + 168
    field(c, fx, fy, "SURNAME", "HALDORSSON")
    field(c, fx, fy + 32, "GIVEN NAMES", "EIRIK MAGNUS")
    field(c, fx, fy + 64, "NATIONALITY", "KESTRIAN")
    field(c, fx, fy + 96, "DATE OF BIRTH", "14 MAR 1987")
    field(c, fx, fy + 128, "PLACE OF BIRTH", "HAVNESTAD, KESTRIA")
    field(c, fx, fy + 160, "SEX", "M")
    # signature + issue / expiry
    sy = py + 382
    c.text(px + 30, sy, "HOLDER'S SIGNATURE", INK_SOFT, 1, 1)
    draw_signature(c, px + 30, sy + 12, 150)
    c.line(px + 30, sy + 32, px + 180, sy + 32, INK, 1)
    field(c, px + 200, sy, "DATE OF ISSUE", "02 JUN 2021")
    field(c, px + 200, sy + 30, "DATE OF EXPIRY", "01 JUN 2031")
    # authority
    ay = py + 448
    c.text(px + 30, ay, "AUTHORITY", INK_SOFT, 1, 1)
    c.text(px + 30, ay + 9, "PASSPORT OFFICE - HAVNESTAD", INK, 2, 1)
    # observations box: the telling detail, cross-referenced to page 2
    oy = py + 492
    c.rect(px + 30, oy, pw - 60, 62, INK_SOFT, 1)
    c.text(px + 40, oy + 8, "OBSERVATIONS", INK_SOFT, 1, 1)
    c.text(px + 40, oy + 22, "HOLDER IS A SEAMAN. SEAMAN'S BOOK NO. 7712.",
           INK, 1, 1)
    c.text(px + 40, oy + 38, "VALID FOR ALL COUNTRIES EXCEPT AS ENDORSED.",
           INK, 1, 1)
    # machine-readable zone
    line1, line2 = mrz_lines()
    mz = py + 580
    c.fill_rect(px + 16, mz, pw - 32, 62, (233, 228, 213))
    c.text(px + 16, mz + 8, line1, INK, 2, 0)
    c.text(px + 16, mz + 32, line2, INK, 2, 0)
    # page number
    c.text(px + pw // 2, py + ph - 30, "1", INK_SOFT, 1, 1, align="center")


def build_visa_page(c, qx, qy, pw, ph, rng):
    c.fill_rect(qx, qy, pw, ph, PAPER)
    guilloche(c, qx + 12, qy + 12, pw - 24, ph - 24, (120, 150, 190), 0.35)
    paper_speckle(c, qx, qy, pw, ph, rng, 500)
    c.rect(qx, qy, pw, ph, INK, 2)
    c.rect(qx + 6, qy + 6, pw - 12, ph - 12, INK_SOFT, 1, 0.7)
    bold_text(c, qx + pw // 2, qy + 26, "VISAS", INK, 2, 1, align="center")
    c.line(qx + 30, qy + 48, qx + pw - 30, qy + 48, INK, 1)
    # Schengen visa sticker
    visa_sticker(c, qx + 30, qy + 62, pw - 60, 168)
    # arrival / departure stamps, each slightly rotated like real ink
    st_y = qy + 262
    c.blit_rotated(circle_stamp("REYKJAVIK", "14 AUG 2022", "ENTRY", 58,
                                STAMP_BLUE), qx + 108, st_y + 62, -8, 0.85)
    c.blit_rotated(rect_stamp([("CAPE TOWN", 1), ("DEPARTURE", 1),
                               ("03 NOV 2022", 1)], 190, 74, STAMP_RED),
                   qx + 330, st_y + 62, 6, 0.85)
    c.blit_rotated(circle_stamp("BUENOS AIRES", "21 JAN 2023", "ENTRY", 58,
                                STAMP_PURPLE), qx + 108, st_y + 212, 9, 0.85)
    c.blit_rotated(rect_stamp([("OSLO", 1), ("EXIT", 1),
                               ("09 MAY 2024", 1)], 190, 74, STAMP_GREEN),
                   qx + 330, st_y + 212, -5, 0.85)
    # seaman's endorsement + harbour tax: the paperwork that tells the story
    ey = qy + 566
    c.blit_rotated(rect_stamp([("SEAMAN'S ENDORSEMENT", 1),
                               ("CREW MEMBER MV SKARVEN", 1),
                               ("SEAMAN'S BOOK NO. 7712", 1),
                               ("HAVNESTAD  02 JUN 2021", 1)],
                              258, 104, STAMP_RED, dashed=True),
                   qx + 158, ey + 52, -4, 0.9)
    c.blit_rotated(rect_stamp([("HARBOUR TAX PAID", 1), ("12 KR", 1),
                               ("02 JUN 2021", 1)], 140, 78, STAMP_GREEN),
                   qx + 372, ey + 42, 8, 0.9)
    # next-of-kin note, in a slanted hand
    c.text(qx + 30, qy + ph - 58,
           "NEXT OF KIN: A. HALDORSSON, HAVNESTAD", INK_SOFT, 1, 1, shear=0.18)
    c.text(qx + pw // 2, qy + ph - 30, "2", INK_SOFT, 1, 1, align="center")


def main():
    rng = random.Random(20261121)
    c = Canvas(1024, 1024, (52, 58, 70))
    # desk: dark slate with faint grain
    for _ in range(2600):
        xx = rng.randint(0, 1023)
        yy = rng.randint(0, 1023)
        c.blend(xx, yy, (70, 78, 94) if rng.random() < 0.5 else (34, 40, 52),
                0.25)
    # soft shadows under the two pages
    draw_shadow(c, 24, 122, 472, 780)
    draw_shadow(c, 528, 122, 472, 780)
    build_data_page(c, 24, 122, 472, 780, rng)
    build_visa_page(c, 528, 122, 472, 780, rng)
    # gutter shadow between the pages
    for i in range(10):
        c.fill_rect(496 + i, 122, 1, 780, (0, 0, 0), 0.05 * (10 - i) / 10)
        c.fill_rect(527 - i, 122, 1, 780, (0, 0, 0), 0.05 * (10 - i) / 10)
    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
    except OSError:
        out = "entry.png"
    size = write_png(c, out)
    print(f"wrote {out} ({size} bytes)")
    line1, line2 = mrz_lines()
    print("MRZ:", line1)
    print("MRZ:", line2)


if __name__ == "__main__":
    main()
