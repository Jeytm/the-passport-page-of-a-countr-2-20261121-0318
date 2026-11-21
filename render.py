#!/usr/bin/env python3
"""Render an invented passport spread for the Republic of Tarnovia.

Draws a 1024x1024 open passport spread: data page (left) with a drawn
portrait, personal data and MRZ; visas/stamps page (right) with a Karnath
entry visa and nine entry/exit stamps telling one coherent travel history.

Everything is invented and drawn in code. Deterministic: no randomness,
no timestamps, no network. Output is byte-identical across runs.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF = os.path.join(FL, "LiberationSerif-Regular.ttf")
SERIF_B = os.path.join(FL, "LiberationSerif-Bold.ttf")
SERIF_I = os.path.join(FL, "LiberationSerif-Italic.ttf")
SANS = os.path.join(FL, "LiberationSans-Regular.ttf")
SANS_B = os.path.join(FL, "LiberationSans-Bold.ttf")
MONO = os.path.join(FD, "DejaVuSansMono.ttf")
MONO_B = os.path.join(FD, "DejaVuSansMono-Bold.ttf")

# ---------------------------------------------------------------- colours
BG = (28, 52, 58)            # dark teal desk
PAGE = (247, 243, 232)       # passport paper
PAGE_EDGE = (226, 219, 198)
INK = (24, 32, 44)           # near-black navy ink
NAVY = (27, 58, 95)
GOLD = (176, 141, 60)
GOLD_LT = (214, 185, 110)
GREY = (105, 108, 105)
RULE = (150, 148, 138)
TEAL = (31, 94, 88)
SAGE = (157, 181, 160)
VISA_BG = (232, 240, 228)
VISA_BD = (94, 128, 84)

# ---------------------------------------------------------------- data
# The invented country: Republic of Tarnovia, landlocked mountain republic.
# Capital Drenovik. Currency: drenar (DRN). Neighbours: Ostrovia (Velmir),
# Karnath (Zorav), Belzara (Porto Lir).
HOLDER = {
    "surname": "KOVAC",
    "given": "MIRA ELENA",
    "nationality": "TARNOVIAN",
    "dob": "14 JUN 1989",
    "pob": "DRENOVIK",
    "sex": "F",
    "issued": "12 MAR 2024",
    "expiry": "12 MAR 2034",
    "number": "TRN 048217",
    "authority": "MINISTRY OF INTERIOR",
}

# Stamps: (kind, place, date). Every date is on/after the 12 MAR 2024
# issue date, and each arrival follows its departure in order.
STAMPS = [
    ("DEPARTURE", "DRENOVIK INTL", "02 APR 2024", NAVY),
    ("ARRIVAL", "VELMIR · OSTROVIA", "02 APR 2024", (96, 54, 120)),
    ("DEPARTURE", "VELMIR", "18 APR 2024", (96, 54, 120)),
    ("ARRIVAL", "ZORAV · KARNATH", "05 MAY 2024", TEAL),
    ("DEPARTURE", "ZORAV", "21 MAY 2024", TEAL),
    ("ARRIVAL", "PORTO LIR · BELZARA", "09 SEP 2025", (122, 60, 46)),
    ("DEPARTURE", "PORTO LIR", "24 SEP 2025", (122, 60, 46)),
    ("ARRIVAL", "VELMIR · OSTROVIA", "14 FEB 2026", (96, 54, 120)),
    ("DEPARTURE", "VELMIR", "28 FEB 2026", (96, 54, 120)),
]
STAMP_ROT = [-5, 4, -3, 5, -4, 3, -6, 4, -3]


# ---------------------------------------------------------------- MRZ (ICAO 9303 check digits)
def _val(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - 55  # A=10 ... Z=35


def _check(s):
    w = (7, 3, 1)
    return str(sum(_val(c) * w[i % 3] for i, c in enumerate(s)) % 10)


def mrz_lines():
    # ICAO 9303 TD3: line 1 = P< + 3-letter issuing state + name (44 chars);
    # line 2 = number(9) + check + nationality(3) + dob(6) + check + sex(1)
    #         + expiry(6) + check + personal number(14) + check + final(1).
    line1 = "P<TRN" + "KOVAC<<MIRA<ELENA"
    line1 = (line1 + "<" * 44)[:44]
    num = "TRN048217"
    num_c = _check(num)
    dob = "890614"
    dob_c = _check(dob)
    exp = "340312"
    exp_c = _check(exp)
    pers = "<" * 14
    pers_c = _check(pers)
    body = num + num_c + "TRN" + dob + dob_c + "F" + exp + exp_c + pers + pers_c
    line2 = body + _check(body)
    return line1, line2


# ---------------------------------------------------------------- helpers
def text(draw, xy, s, fnt, fill=INK, anchor="la"):
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def centre(draw, cx, y, s, fnt, fill=INK):
    draw.text((cx, y), s, font=fnt, fill=fill, anchor="ma")


def coat_of_arms(draw, cx, cy, s):
    """Shield with three mountain peaks and a star, navy + gold."""
    w, h = s, int(s * 1.15)
    x0, y0 = cx - w // 2, cy - h // 2
    shield = [
        (x0, y0), (x0 + w, y0), (x0 + w, y0 + int(h * 0.62)),
        (cx, y0 + h), (x0, y0 + int(h * 0.62)),
    ]
    draw.polygon(shield, fill=(232, 226, 200), outline=NAVY, width=3)
    # mountains
    base = y0 + int(h * 0.78)
    draw.polygon(
        [(x0 + 8, base), (x0 + int(w * 0.32), y0 + int(h * 0.30)),
         (x0 + int(w * 0.55), base)], fill=TEAL)
    draw.polygon(
        [(x0 + int(w * 0.42), base), (x0 + int(w * 0.68), y0 + int(h * 0.18)),
         (x0 + int(w * 0.94) - 8, base)], fill=NAVY)
    # snowcaps
    draw.polygon(
        [(x0 + int(w * 0.32), y0 + int(h * 0.30)),
         (x0 + int(w * 0.26), y0 + int(h * 0.42)),
         (x0 + int(w * 0.38), y0 + int(h * 0.42))], fill=(247, 243, 232))
    draw.polygon(
        [(x0 + int(w * 0.68), y0 + int(h * 0.18)),
         (x0 + int(w * 0.62), y0 + int(h * 0.30)),
         (x0 + int(w * 0.74), y0 + int(h * 0.30))], fill=(247, 243, 232))
    # star above peaks
    sx, sy, r = cx, y0 + 12, 7
    star = []
    import math
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(star, fill=GOLD)


def draw_portrait(draw, box):
    """Flat-illustration portrait of the holder, drawn in code.

    Rendered on its own layer first so the security arcs behind the head
    stay inside the photo frame instead of bleeding over the page header.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGB", (w, h), SAGE)
    d = ImageDraw.Draw(layer)
    # faint guilloche arcs behind the head (clipped to the frame)
    for r in range(20, 130, 14):
        d.arc([80 - r, 78 - r, 80 + r, 78 + r],
              200, 340, fill=(139, 165, 144), width=1)
    cx = w // 2
    # shoulders / jacket
    d.polygon([(cx - 62, h), (cx - 58, h - 42), (cx - 26, h - 52),
               (cx + 26, h - 52), (cx + 58, h - 42), (cx + 62, h)],
              fill=(52, 74, 92))
    d.polygon([(cx - 14, h - 50), (cx, h - 34), (cx + 14, h - 50),
               (cx, h)], fill=(232, 226, 200))
    # neck + face
    d.rectangle([cx - 11, h - 66, cx + 11, h - 46], fill=(216, 178, 140))
    d.ellipse([cx - 34, 26, cx + 34, 104], fill=(226, 188, 152))
    # hair: dark bob framing the face
    d.pieslice([cx - 40, 16, cx + 40, 96], 180, 360, fill=(58, 40, 30))
    d.ellipse([cx - 40, 16, cx + 40, 92], fill=(58, 40, 30))
    d.ellipse([cx - 34, 26, cx + 34, 104], fill=(226, 188, 152))
    d.arc([cx - 34, 26, cx + 34, 78], 180, 360, fill=(58, 40, 30), width=10)
    # brows, eyes, nose, mouth
    d.line([cx - 22, 62, cx - 8, 60], fill=(58, 40, 30), width=2)
    d.line([cx + 8, 60, cx + 22, 62], fill=(58, 40, 30), width=2)
    d.ellipse([cx - 19, 66, cx - 11, 72], fill=(40, 32, 26))
    d.ellipse([cx + 11, 66, cx + 19, 72], fill=(40, 32, 26))
    d.line([cx, 70, cx - 2, 82], fill=(198, 152, 116), width=2)
    d.arc([cx - 9, 86, cx + 9, 96], 15, 165, fill=(150, 84, 70), width=2)
    draw._image.paste(layer, (x0, y0))


def stamp_layer(kind, place, date, colour, rot):
    """One entry/exit stamp on its own transparent layer, rotated.

    The layer is exactly one grid cell (160x100) and the stamp itself is
    140x72, so neighbouring stamps in the grid never overlap each other.
    """
    sw, sh = 140, 72
    layer = Image.new("RGBA", (160, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = 10, 14
    ink = colour + (215,)
    d.rounded_rectangle([x0, y0, x0 + sw, y0 + sh], radius=8,
                        outline=ink, width=3)
    d.line([x0 + 10, y0 + 26, x0 + sw - 10, y0 + 26], fill=ink, width=1)
    d.line([x0 + 10, y0 + 48, x0 + sw - 10, y0 + 48], fill=ink, width=1)
    centre(d, x0 + sw // 2, y0 + 4, kind, font(SANS_B, 15), fill=ink)
    # place line: shrink the font until it fits inside the stamp
    psize = 13
    while psize > 9 and d.textlength(place, font=font(SANS_B, psize)) > sw - 16:
        psize -= 1
    centre(d, x0 + sw // 2, y0 + 28, place, font(SANS_B, psize), fill=ink)
    centre(d, x0 + sw // 2, y0 + 50, date, font(SANS, 13), fill=ink)
    return layer.rotate(rot, resample=Image.BICUBIC, expand=False)


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")

    # soft vignette on the desk
    for i in range(60):
        a = 10 - i // 8
        d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=(0, 0, 0, a))

    # the two pages
    for (px0, px1) in [(24, 502), (522, 1000)]:
        d.rectangle([px0 + 4, 60, px1 + 4, 968], fill=(0, 0, 0, 70))
        d.rectangle([px0, 56, px1, 964], fill=PAGE, outline=PAGE_EDGE, width=1)
    # centre fold shadow
    d.rectangle([502, 56, 522, 964], fill=(0, 0, 0, 26))

    # ================================================= LEFT PAGE (data)
    lx0, lx1 = 24, 502
    cx = (lx0 + lx1) // 2

    coat_of_arms(d, cx, 128, 56)
    centre(d, cx, 168, "REPUBLIC OF TARNOVIA", font(SERIF_B, 27), NAVY)
    centre(d, cx, 200, "R E P U B L I K A   T A R N O V I J A",
           font(SANS, 11), GREY)
    d.line([lx0 + 40, 228, lx1 - 40, 228], fill=RULE, width=1)
    centre(d, cx, 236, "PASSPORT  ·  PUTOVNICA", font(SANS_B, 12), NAVY)

    # photo
    photo = (lx0 + 28, 268, lx0 + 188, 428)
    draw_portrait(d, photo)
    d.rectangle(photo, outline=NAVY, width=2)
    centre(d, (photo[0] + photo[2]) // 2, 432, "PHOTO", font(SANS, 9), GREY)

    # data fields, right of the photo
    fx = lx0 + 206
    fields = [
        ("SURNAME", HOLDER["surname"]),
        ("GIVEN NAMES", HOLDER["given"]),
        ("NATIONALITY", HOLDER["nationality"]),
        ("DATE OF BIRTH", HOLDER["dob"]),
        ("PLACE OF BIRTH", HOLDER["pob"]),
        ("SEX", HOLDER["sex"]),
    ]
    y = 268
    for label, value in fields:
        text(d, (fx, y), label, font(SANS, 9), GREY)
        text(d, (fx, y + 11), value, font(SANS_B, 16))
        y += 30

    # second row of fields, full width
    y = 470
    row2 = [
        ("PASSPORT NO.", HOLDER["number"], lx0 + 28),
        ("DATE OF ISSUE", HOLDER["issued"], lx0 + 190),
        ("DATE OF EXPIRY", HOLDER["expiry"], lx0 + 348),
    ]
    for label, value, x in row2:
        text(d, (x, y), label, font(SANS, 9), GREY)
        text(d, (x, y + 11), value, font(SANS_B, 15))
    y = 528
    text(d, (lx0 + 28, y), "AUTHORITY", font(SANS, 9), GREY)
    text(d, (lx0 + 28, y + 11), HOLDER["authority"] + " — DRENOVIK",
         font(SANS_B, 15))
    text(d, (lx0 + 28, y + 34), "HOLDER'S SIGNATURE",
         font(SANS, 9), GREY)
    # signature in script-like italic
    text(d, (lx0 + 28, y + 45), "Mira Elena Kovac",
         font(SERIF_I, 20), (52, 58, 96))
    d.line([lx0 + 28, y + 70, lx0 + 260, y + 70], fill=RULE, width=1)

    # trilingual note
    ny = 640
    centre(d, cx, ny,
           "This passport is the property of the Republic of Tarnovia.",
           font(SERIF_I, 11), GREY)
    centre(d, cx, ny + 16,
           "Ova putovnica je vlasništvo Republike Tarnovije.",
           font(SERIF_I, 11), GREY)
    centre(d, cx, ny + 32,
           "Ce passeport est la propriété de la République de Tarnovie.",
           font(SERIF_I, 11), GREY)

    # MRZ band
    d.rectangle([lx0 + 20, 700, lx1 - 20, 772], fill=(238, 234, 220))
    d.line([lx0 + 20, 700, lx1 - 20, 700], fill=RULE, width=1)
    d.line([lx0 + 20, 772, lx1 - 20, 772], fill=RULE, width=1)
    l1, l2 = mrz_lines()
    text(d, (lx0 + 32, 712), l1, font(MONO, 15))
    text(d, (lx0 + 32, 738), l2, font(MONO, 15))

    # page footer
    centre(d, cx, 800, "TARNOVIA  ·  DRENOVIK  ·  EST. 1921",
           font(SANS, 10), GREY)
    centre(d, cx, 920, "1", font(SERIF, 12), GREY)

    # ================================================= RIGHT PAGE (visas)
    rx0, rx1 = 522, 1000
    rcx = (rx0 + rx1) // 2
    centre(d, rcx, 76, "V I S A S", font(SERIF_B, 20), NAVY)
    d.line([rx0 + 40, 106, rx1 - 40, 106], fill=RULE, width=1)

    # Karnath entry visa sticker
    vx0, vy0, vx1, vy1 = rx0 + 28, 122, rx1 - 28, 322
    d.rounded_rectangle([vx0, vy0, vx1, vy1], radius=6,
                        fill=VISA_BG, outline=VISA_BD, width=2)
    d.rounded_rectangle([vx0 + 5, vy0 + 5, vx1 - 5, vy0 + 44], radius=4,
                        fill=TEAL)
    centre(d, rcx, vy0 + 12, "KARNATH  —  ENTRY VISA",
           font(SANS_B, 16), (247, 243, 232))
    vrows = [
        ("TYPE", "C  ·  SINGLE ENTRY"),
        ("VALID", "01 MAY 2024  –  30 JUN 2024"),
        ("ISSUED", "22 APR 2024  ·  DRENOVIK"),
        ("FEE", "45 DRN  —  PAID"),
    ]
    vy = vy0 + 58
    for label, value in vrows:
        text(d, (vx0 + 16, vy), label, font(SANS_B, 11), TEAL)
        text(d, (vx0 + 96, vy), value, font(SANS_B, 14))
        vy += 26
    text(d, (vx0 + 16, vy + 2),
         "CONDITIONS:  VALID FOR MOUNTAIN PASSES ONLY.",
         font(SANS_B, 12), (122, 60, 46))
    text(d, (vx0 + 16, vy + 20),
         "COASTAL ROAD CLOSED TO VISITORS.",
         font(SANS_B, 12), (122, 60, 46))

    # circular fee stamp: bottom-right of the visa page, clear of the
    # visa sticker and the request text
    fee = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fee)
    fd.ellipse([10, 10, 140, 140], outline=(122, 60, 46, 220), width=3)
    fd.ellipse([22, 22, 128, 128], outline=(122, 60, 46, 220), width=1)
    centre(fd, 75, 42, "VISA FEE", font(SANS_B, 13),
           fill=(122, 60, 46, 220))
    centre(fd, 75, 62, "PAID", font(SANS_B, 17),
           fill=(122, 60, 46, 220))
    centre(fd, 75, 86, "45 DRN", font(SANS_B, 13),
           fill=(122, 60, 46, 220))
    fee = fee.rotate(-14, resample=Image.BICUBIC)
    img.paste(fee, (rx1 - 185, 772), fee)
    d = ImageDraw.Draw(img, "RGBA")

    # stamps grid: 3 columns x 3 rows
    gx, gy = rx0 + 26, 356
    for i, (kind, place, date, colour) in enumerate(STAMPS):
        col, row = i % 3, i // 3
        layer = stamp_layer(kind, place, date, colour, STAMP_ROT[i])
        img.paste(layer, (gx + col * 152 - 4, gy + row * 96 - 2), layer)
        d = ImageDraw.Draw(img, "RGBA")

    # request text at the foot of the visa page
    fy = 700
    centre(d, rcx, fy,
           "The Ministry of Foreign Affairs of the Republic of Tarnovia",
           font(SERIF_I, 12), GREY)
    centre(d, rcx, fy + 18,
           "requests all whom it may concern to allow the bearer",
           font(SERIF_I, 12), GREY)
    centre(d, rcx, fy + 36,
           "to pass freely and to afford all lawful assistance.",
           font(SERIF_I, 12), GREY)
    centre(d, rcx, 920, "2", font(SERIF, 12), GREY)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    img = render()
    img.save(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
