#!/usr/bin/env python3
"""Draw news-image-20261125 v2: a dense one-day front page in the style of the
top-ranked news-image entries (date as headline, region bar, badges, UTC
timeline, IN NUMBERS, map with pins, red DATE CHECK). All 46 stories are
real events of Wednesday 25 November 2026 (UTC). No network access.
Deterministic: identical input -> byte-identical PNG."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (245, 239, 224)      # beige paper
INK = (20, 20, 20)
GREY = (95, 95, 95)
RULE = (190, 178, 150)
RED = (176, 58, 46)
NAVY = (31, 58, 95)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fnt, max_w):
    """Single line; truncate with an ellipsis if it does not fit."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "\u2026", font=fnt) > max_w:
        text = text[:-1]
    return text + "\u2026"


# ---------------- data ----------------
# (short label, count, colour)
REGIONS = [
    ("N AMERICA", 6, "#b03a2e"),
    ("EUROPE", 9, "#1f618d"),
    ("MID EAST", 5, "#7d6608"),
    ("ASIA-PAC", 8, "#196f4e"),
    ("AFRICA", 4, "#7b4a1f"),
    ("LATIN AM", 4, "#6c3483"),
    ("BUSINESS", 6, "#333333"),
    ("TECH", 2, "#2e5a88"),
    ("SPORT", 2, "#8a2a2a"),
]

TIMELINE = [
    ("00:19", "Shenzhou-24 lifts off"),
    ("00:30", "Australia CPI 4.9% beats forecast"),
    ("03:56", "Shenzhou-24 docks at Tiangong"),
    ("13:30", "US PCE 3.8%; GDP revised to 4.3%"),
    ("14:30", "Wall Street opens lower on tariffs"),
    ("21:00", "Dow closes above 50,000"),
]

NUMBERS = [
    ("14", "trading partners face new US tariffs"),
    ("$227m", "of meth seized in Nigeria"),
    ("1.3m", "Hong Kong ticketing users' data leaked"),
    ("$50bn", "EU quantum investment plan"),
    ("81.5m", "Americans travelling for Thanksgiving"),
    ("4", "tankers hit by mines off Hormuz"),
]

# badge codes: C CONFIRMED (2+ outlets), O OFFICIAL, R REPORTED (single outlet),
# CL CLAIM (attributed), OG ONGOING
BIG3 = [
    ("US proposes tariffs on 14 partners", "C",
     "Rates of 20-40%; the EU faces 15% on top of existing duties. Hearing set for 25 January.",
     "tariffs"),
    ("Shenzhou-24 carries first foreign astronaut", "C",
     "Pakistan's Muhammad Zeeshan Ali joins the two-man Chinese crew bound for Tiangong.",
     "rocket"),
    ("Riyadh skyscraper struck for second time", "C",
     "Saudi capital's tallest tower hit again in days; at least 11 people injured.",
     "tower"),
]

# (headline, badge, icon kind)
CARDS10 = [
    ("Merz: Europe will show Russia its limits", "C", "shield"),
    ("Huawei guilty of trade-secret theft plot", "C", "chip"),
    ("China opens shock probe into Politburo member", "C", "lens"),
    ("Israeli strike kills Hamas colonel in Gaza", "C", "blast"),
    ("Iran says four tankers hit mines off Hormuz", "CL", "ship"),
    ("Wall Street slides on tariff fears", "C", "chart"),
    ("CIA and spy chief hit by cyber breach", "R", "laptop"),
    ("Hong Kong pledges HK$630m for fire-hit estate", "C", "building"),
    ("Nigeria seizes $227m of meth", "C", "box"),
    ("Barcelona hit four; Bayern stunned in Europe", "C", "ball"),
]

# (headline, badge) — numbers 14..46, grouped by region
ALSO = [
    ("US consumer confidence jumps", "C"),
    ("Trump awards Giuliani Medal of Freedom", "O"),
    ("US soldier admits selling secrets to China", "R"),
    ("Three killed in overnight Russia-Ukraine strikes", "C"),
    ("EU warns 11 states over spending rules", "C"),
    ("EU parliament votes to loosen nature laws", "C"),
    ("EU unveils \u20ac50bn quantum investment plan", "C"),
    ("Pope Leo XIV laments COP31 failure", "C"),
    ("Met Police still institutionally racist", "O"),
    ("Denmark bans headscarves for prosecutors", "O"),
    ("France approves 2026 year-end budget", "O"),
    ("US tells citizens to leave Iran", "C"),
    ("Houthis claim strike on Saudi refinery", "CL"),
    ("Australia signs security pact with Solomons", "C"),
    ("North Korea expels top Swiss diplomat", "R"),
    ("Data of 1.3m Hong Kong ticketing users leaked", "C"),
    ("Australia inflation hotter than expected", "O"),
    ("Africa Cup title handed back to Senegal", "C"),
    ("South Africa backs police chief to lead Hawks", "R"),
    ("Sudan drone strikes kill 19 civilians", "R"),
    ("Brazil police freeze $340m in ore probe", "C"),
    ("Storms kill six in southern Brazil", "C"),
    ("Gunmen free 10 hostages in Colombia", "R"),
    ("Ecuador vote campaign ends in silence", "R"),
    ("Bitcoin funds head for worst month", "C"),
    ("India's Sensex pares gains, rupee surges", "C"),
    ("Flipkart chief to step down after a decade", "C"),
    ("Huang says he is in therapy as Nvidia fades", "R"),
    ("Advent weighs bid for Bureau Veritas", "R"),
    ("US inflation 3.8% as GDP revised to 4.3%", "R"),
    ("New Asian maths body launches in Hong Kong", "C"),
    ("Europe's biggest satellite factory opens", "C"),
    ("Sinner doubtful for Australian Open", "C"),
]

DATE_CHECK = [
    ("23 Nov", "COP31 climate talks collapse with no deal"),
    ("23 Nov", "Kyiv region declares day of mourning after Russian strikes"),
    ("22 Nov", "Sudan drone strikes kill children in Khartoum"),
    ("20 Nov", "GTA VI day-one sales figure"),
    ("23 Nov", "Maduro birthday"),
]

BADGE_FILL = {
    "C": (25, 111, 61),
    "O": (31, 97, 141),
    "R": (125, 102, 8),
    "CL": (176, 58, 46),
    "OG": (108, 52, 131),
}

# simplified continents, (lon, lat) polygons
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-80, 73), (-70, 62), (-65, 60), (-55, 52), (-60, 46), (-70, 44),
     (-75, 38), (-80, 32), (-81, 26), (-90, 21), (-97, 16), (-105, 20),
     (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-80, -5), (-81, -15), (-75, -25), (-70, -35),
     (-65, -45), (-68, -52), (-60, -55), (-55, -35), (-50, -30), (-40, -20),
     (-35, -8), (-40, 0), (-50, 5), (-60, 8), (-70, 11)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 58), (10, 59), (18, 56),
     (21, 55), (28, 60), (30, 62), (25, 66), (30, 70), (40, 68), (45, 60),
     (40, 55), (35, 50), (30, 46), (28, 44), (23, 40), (19, 42), (12, 44),
     (8, 44), (3, 42), (-2, 37)],
    [(-6, 35), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28), (37, 22),
     (40, 15), (43, 11), (48, 10), (51, 12), (45, 5), (41, -2), (40, -10),
     (35, -18), (32, -26), (28, -33), (20, -35), (15, -28), (12, -18),
     (13, -10), (9, -2), (9, 4), (0, 6), (-8, 5), (-15, 11), (-17, 15),
     (-16, 20), (-15, 28)],
    [(30, 70), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (160, 66), (170, 66), (178, 65), (170, 60), (160, 60),
     (155, 55), (145, 45), (140, 40), (135, 35), (130, 33), (127, 40),
     (122, 38), (120, 32), (115, 25), (110, 20), (108, 12), (105, 8),
     (100, 7), (98, 12), (95, 16), (92, 21), (88, 22), (85, 19), (80, 13),
     (77, 8), (73, 15), (70, 20), (66, 25), (60, 25), (57, 26), (52, 28),
     (50, 29), (48, 30), (44, 29), (40, 30), (38, 32), (36, 36), (33, 36),
     (30, 40), (28, 42), (30, 46), (32, 50), (35, 55), (40, 60)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

# (lat, lon) for the 13 featured stories (pins 1-13); small offsets keep
# the two near-duplicate pairs (Washington/Langley, Shenzhen/Hong Kong) apart
PINS = [
    (38.9, -77.0), (40.9, 100.3), (24.7, 46.7), (52.5, 13.4),
    (23.5, 114.8), (39.9, 116.4), (31.5, 34.5), (26.5, 56.3),
    (40.7, -74.0), (39.6, -77.9), (22.3, 113.0), (6.5, 7.5), (41.4, 2.2),
]

# pixel offsets (dx, dy) for pins that would otherwise collide on the map;
# a thin leader line joins the offset pin to its true spot
PIN_OFFSETS = {1: (-18, 14), 9: (2, -18), 10: (18, 10), 5: (16, -14),
               11: (-16, 14)}


# ---------------- drawing helpers ----------------
def badge(d, x, y, code, fnt):
    """Badge circle (pill for CL) at top-left (x, y). Returns width used."""
    fill = BADGE_FILL[code]
    if code == "CL":
        d.rounded_rectangle([x, y, x + 24, y + 16], radius=8, fill=fill)
        d.text((x + 5, y + 2), code, font=fnt, fill="white")
        return 26
    d.ellipse([x, y, x + 16, y + 16], fill=fill)
    tw = d.textlength(code, font=fnt)
    d.text((x + (16 - tw) / 2, y + 2), code, font=fnt, fill="white")
    return 18


def draw_icon(d, kind, x, y, w, h):
    """Small flat icon inside box (x, y, w, h)."""
    cx, cy = x + w // 2, y + h // 2
    if kind == "shield":  # EU shield + star
        d.polygon([(cx - 12, cy - 14), (cx + 12, cy - 14), (cx + 12, cy + 2),
                   (cx, cy + 15), (cx - 12, cy + 2)], fill=(31, 97, 141))
        d.regular_polygon((cx, cy - 4, 5), 5, fill=(240, 200, 60))
    elif kind == "chip":
        d.rectangle([cx - 13, cy - 10, cx + 13, cy + 10], fill=(40, 40, 40))
        d.rectangle([cx - 6, cy - 4, cx + 6, cy + 4], fill=(240, 200, 60))
        for dx in (-9, 0, 9):
            d.line([(cx + dx, cy - 14), (cx + dx, cy - 10)], fill=(40, 40, 40), width=2)
            d.line([(cx + dx, cy + 10), (cx + dx, cy + 14)], fill=(40, 40, 40), width=2)
    elif kind == "lens":  # magnifier
        d.ellipse([cx - 11, cy - 13, cx + 5, cy + 3], outline=RED, width=3)
        d.line([(cx + 3, cy + 1), (cx + 12, cy + 12)], fill=RED, width=3)
    elif kind == "blast":
        pts = []
        import math
        for i in range(12):
            ang = math.pi * i / 6
            r = 14 if i % 2 == 0 else 6
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=(230, 120, 30))
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 220, 80))
    elif kind == "ship":
        d.polygon([(cx - 16, cy + 2), (cx + 16, cy + 2), (cx + 11, cy + 12),
                   (cx - 11, cy + 12)], fill=(31, 58, 95))
        d.rectangle([cx - 10, cy - 8, cx - 2, cy + 2], fill=(176, 58, 46))
        d.rectangle([cx, cy - 8, cx + 8, cy + 2], fill=(25, 111, 61))
        d.rectangle([cx + 8, cy - 6, cx + 13, cy + 2], fill=(125, 102, 8))
    elif kind == "chart":
        d.line([(cx - 14, cy + 12), (cx + 14, cy + 12)], fill=INK, width=2)
        d.line([(cx - 14, cy + 12), (cx - 14, cy - 12)], fill=INK, width=2)
        d.line([(cx - 12, cy - 6), (cx - 4, cy + 0), (cx + 4, cy - 2),
                (cx + 12, cy + 10)], fill=RED, width=3)
        d.polygon([(cx + 12, cy + 10), (cx + 6, cy + 8), (cx + 12, cy + 4)],
                  fill=RED)
    elif kind == "laptop":
        d.rectangle([cx - 13, cy - 10, cx + 13, cy + 6], fill=(40, 40, 40))
        d.rectangle([cx - 10, cy - 7, cx + 10, cy + 3], fill=(200, 220, 235))
        d.polygon([(cx, cy - 5), (cx - 5, cy + 2), (cx + 5, cy + 2)], fill=RED)
        d.line([(cx - 16, cy + 9), (cx + 16, cy + 9)], fill=(40, 40, 40), width=3)
    elif kind == "building":
        d.rectangle([cx - 10, cy - 13, cx + 2, cy + 12], fill=(90, 90, 90))
        d.rectangle([cx + 4, cy - 6, cx + 13, cy + 12], fill=(140, 140, 140))
        for wy in (-8, -2, 4):
            d.rectangle([cx - 7, cy + wy, cx - 3, cy + wy + 3], fill=(245, 239, 224))
        d.polygon([(cx - 2, cy - 16), (cx + 8, cy - 16), (cx + 3, cy - 10)],
                  fill=RED)
    elif kind == "box":
        d.polygon([(cx - 13, cy - 4), (cx, cy - 12), (cx + 13, cy - 4),
                   (cx + 13, cy + 10), (cx - 13, cy + 10)], fill=(150, 100, 40))
        d.line([(cx, cy - 12), (cx, cy + 10)], fill=(120, 75, 25), width=2)
        d.line([(cx - 13, cy - 4), (cx + 13, cy - 4)], fill=(120, 75, 25), width=2)
    elif kind == "ball":
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=INK, width=2,
                  fill="white")
        d.regular_polygon((cx, cy, 5), 5, fill=INK)
        for ang in (0, 72, 144, 216, 288):
            import math
            a = math.radians(ang)
            d.line([(cx + 5 * math.cos(a), cy + 5 * math.sin(a)),
                    (cx + 12 * math.cos(a), cy + 12 * math.sin(a))],
                   fill=INK, width=1)


def draw_scene(d, kind, x, y, w, h):
    """Flat scene for a big story inside box (x, y, w, h)."""
    if kind == "tariffs":
        d.rectangle([x, y, x + w, y + h], fill=NAVY)
        # capitol dome silhouette
        d.polygon([(x + 28, y + 26), (x + 28, y + h - 6), (x + 82, y + h - 6),
                   (x + 82, y + 26)], fill="white")
        d.pieslice([x + 28, y + 6, x + 82, y + 34], 180, 360, fill="white")
        d.rectangle([x + 52, y + 0, x + 58, y + 8], fill="white")
        d.rectangle([x + 38, y + 34, x + 44, y + h - 6], fill=NAVY)
        d.rectangle([x + 66, y + 34, x + 72, y + h - 6], fill=NAVY)
        # crates with % tags
        for i, tag in enumerate(("20%", "40%", "15%")):
            cx0 = x + 120 + i * 62
            d.rectangle([cx0, y + h - 30, cx0 + 48, y + h - 6],
                        fill=(214, 178, 110), outline=(120, 85, 40), width=1)
            d.text((cx0 + 8, y + h - 24), tag, font=font(SANS_B, 12), fill=INK)
        d.text((x + 120, y + 8), "TARIFFS ON 14 PARTNERS", font=font(SANS_B, 12),
               fill=(240, 200, 60))
    elif kind == "rocket":
        d.rectangle([x, y, x + w, y + h], fill=(12, 20, 40))
        for sx, sy in [(x + 250, y + 10), (x + 280, y + 22), (x + 235, y + 30),
                       (x + 265, y + 40), (x + 295, y + 8)]:
            d.regular_polygon((sx, sy, 2), 4, fill="white")
        # station: hub + panels
        d.rectangle([x + 200, y + 22, x + 260, y + 34], fill=(160, 160, 160))
        d.rectangle([x + 168, y + 24, x + 200, y + 32], fill=(31, 97, 141))
        d.rectangle([x + 260, y + 24, x + 292, y + 32], fill=(31, 97, 141))
        # rocket
        d.polygon([(x + 60, y + 6), (x + 74, y + 6), (x + 74, y + 44),
                   (x + 60, y + 44)], fill="white")
        d.polygon([(x + 60, y + 6), (x + 67, y - 4), (x + 74, y + 6)],
                  fill=RED)
        d.polygon([(x + 60, y + 36), (x + 50, y + 48), (x + 60, y + 44)],
                  fill=RED)
        d.polygon([(x + 74, y + 36), (x + 84, y + 48), (x + 74, y + 44)],
                  fill=RED)
        d.polygon([(x + 62, y + 44), (x + 72, y + 44), (x + 67, y + h - 4)],
                  fill=(255, 170, 40))
        d.text((x + 100, y + 8), "FIRST FOREIGN", font=font(SANS_B, 12),
               fill="white")
        d.text((x + 100, y + 24), "ASTRONAUT", font=font(SANS_B, 12),
               fill="white")
    elif kind == "tower":
        d.rectangle([x, y, x + w, y + h], fill=(226, 220, 205))
        # smoke puffs
        for sx, sy, r in [(x + 90, y + 12, 10), (x + 110, y + 6, 8),
                          (x + 128, y + 14, 9), (x + 70, y + 18, 7)]:
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(150, 150, 150))
        # tower
        d.polygon([(x + 96, y + 20), (x + 122, y + 20), (x + 118, y + h),
                   (x + 100, y + h)], fill=(60, 60, 60))
        for wy in range(y + 28, y + h - 6, 10):
            d.rectangle([x + 103, wy, x + 115, wy + 4], fill=(240, 200, 60))
        d.text((x + 150, y + 10), "11 INJURED", font=font(SANS_B, 13), fill=RED)
        d.text((x + 150, y + 28), "SECOND STRIKE", font=font(SANS_B, 11),
               fill=INK)
        d.text((x + 150, y + 44), "IN DAYS", font=font(SANS_B, 11), fill=INK)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 24                      # margin
    CW = W - 2 * M              # content width 976

    f_kick = font(SANS_B, 13)
    f_head = font(SERIF_B, 52)
    f_sub = font(SANS, 13)
    f_bar = font(SANS_B, 8)
    f_tl = font(SANS_B, 11)
    f_tlt = font(SANS, 10)
    f_num = font(SANS_B, 20)
    f_numl = font(SANS, 9)
    f_big_h = font(SANS_B, 14)
    f_big_s = font(SANS, 11)
    f_card = font(SANS_B, 11)
    f_also_h = font(SANS_B, 11)
    f_also = font(SANS, 11)
    f_badge = font(SANS_B, 9)
    f_sec = font(SANS_B, 11)
    f_dc = font(SANS, 10)
    f_dc_t = font(SANS_B, 12)
    f_leg = font(SANS, 9)
    f_foot = font(SANS, 10)

    d.rectangle([5, 5, W - 6, H - 6], outline=INK, width=3)

    # ---- kicker ----
    d.text((M, 12), "ONE DAY OF WORLD NEWS", font=f_kick, fill=RED)
    right = "46 STORIES  \u00b7  9 REGIONS  \u00b7  20 FIELDS  \u00b7  EVERY ONE FROM WEDNESDAY 25 NOVEMBER 2026"
    tw = d.textlength(right, font=font(SANS_B, 10))
    d.text((W - M - tw, 14), right, font=font(SANS_B, 10), fill=INK)

    # ---- headline: the date itself ----
    title = "Wednesday 25 November 2026"
    tw = d.textlength(title, font=f_head)
    d.text(((W - tw) / 2, 32), title, font=f_head, fill=INK)
    sub = ("Tariffs on 14 partners \u00b7 Shenzhou-24 carries a first foreign astronaut "
           "\u00b7 Riyadh's tallest tower struck again")
    tw = d.textlength(sub, font=f_sub)
    d.text(((W - tw) / 2, 92), sub, font=f_sub, fill=GREY)
    d.line([(M, 110), (W - M, 110)], fill=INK, width=2)

    # ---- region bar ----
    bx, by = M, 116
    total = sum(c for _, c, _ in REGIONS)
    for label, count, color in REGIONS:
        seg_w = CW * count / total
        d.rectangle([bx, by, bx + seg_w - 1, by + 20], fill=color)
        txt = f"{label} {count}"
        tw = d.textlength(txt, font=f_bar)
        if tw <= seg_w - 4:
            d.text((bx + (seg_w - tw) / 2, by + 5), txt, font=f_bar, fill="white")
        bx += seg_w

    # ---- UTC timeline ----
    d.text((M, 144), "THE DAY IN UTC", font=f_tl, fill=RED)
    tl_x = M + 118
    tl_w = (W - M - tl_x)
    col_w = tl_w / len(TIMELINE)
    d.line([(tl_x, 168), (W - M, 168)], fill=RULE, width=1)
    for i, (t, text) in enumerate(TIMELINE):
        x = tl_x + i * col_w
        d.ellipse([x + 2, 164, x + 10, 172], fill=RED)
        d.text((x + 14, 142), t, font=f_tl, fill=RED)
        lines = wrap(d, text, f_tlt, col_w - 16)
        yy = 156
        for line in lines[:2]:
            d.text((x + 14, yy), line, font=f_tlt, fill=INK)
            yy += 11
    assert yy <= 180, "timeline overflow"

    # ---- IN NUMBERS ----
    d.line([(M, 184), (W - M, 184)], fill=INK, width=1)
    d.text((M, 190), "IN NUMBERS", font=f_tl, fill=RED)
    num_x = M + 108
    num_w = (W - M - num_x) / len(NUMBERS)
    for i, (val, label) in enumerate(NUMBERS):
        x = num_x + i * num_w
        d.text((x, 188), val, font=f_num, fill=INK)
        lines = wrap(d, label, f_numl, num_w - 8)
        yy = 188 + 22
        for line in lines[:2]:
            d.text((x, yy), line, font=f_numl, fill=GREY)
            yy += 10
    d.line([(M, 232), (W - M, 232)], fill=INK, width=1)

    # ---- big three ----
    big_y = 240
    big_w = (CW - 2 * 12) // 3
    for i, (headline, bdg, summary, scene) in enumerate(BIG3):
        x = M + i * (big_w + 12)
        draw_scene(d, scene, x, big_y, big_w, 56)
        badge(d, x + big_w - 20, big_y + 4, bdg, f_badge)
        hl = wrap(d, headline, f_big_h, big_w - 4)
        yy = big_y + 62
        for line in hl[:2]:
            d.text((x + 2, yy), line, font=f_big_h, fill=INK)
            yy += 16
        sl = wrap(d, summary, f_big_s, big_w - 4)
        for line in sl[:2]:
            d.text((x + 2, yy), line, font=f_big_s, fill=(40, 40, 40))
            yy += 12
        assert yy <= big_y + 118, f"big story {i + 1} overflow"

    # ---- small cards 5x2 ----
    card_y = 366
    card_w = (CW - 4 * 10) // 5
    card_h = 46
    for i, (headline, bdg, icon) in enumerate(CARDS10):
        r, c = divmod(i, 5)
        x = M + c * (card_w + 10)
        y = card_y + r * (card_h + 6)
        d.rounded_rectangle([x, y, x + card_w, y + card_h], radius=4,
                            fill=(238, 231, 210), outline=RULE, width=1)
        draw_icon(d, icon, x + 4, y + 5, 44, 36)
        tx = x + 52
        lines = wrap(d, headline, f_card, card_w - 56)
        yy = y + 5
        for line in lines[:3]:
            d.text((tx, yy), line, font=f_card, fill=INK)
            yy += 13
        badge(d, x + card_w - 20, y + card_h - 20, bdg, f_badge)

    # ---- ALSO list ----
    also_y = 474
    d.text((M, also_y), "ALSO ON WEDNESDAY 25 NOVEMBER  \u00b7  33 MORE, BY REGION",
           font=f_sec, fill=INK)
    d.line([(M, also_y + 16), (W - M, also_y + 16)], fill=INK, width=1)
    list_y = also_y + 22
    list_col_w = (CW - 2 * 12) // 3
    rows = 11
    for idx, (headline, bdg) in enumerate(ALSO):
        col, row = divmod(idx, rows)
        x = M + col * (list_col_w + 12)
        y = list_y + row * 25
        num = f"{idx + 14}."
        d.text((x, y), num, font=f_also_h, fill=RED)
        nw = d.textlength(num, font=f_also_h)
        max_w = list_col_w - nw - 8 - 24
        txt = fit(d, headline, f_also, max_w)
        d.text((x + nw + 4, y), txt, font=f_also, fill=INK)
        badge(d, x + list_col_w - 18, y - 1, bdg, f_badge)

    # ---- map + DATE CHECK ----
    bot_y = 758
    d.text((M, bot_y), "WHERE IT HAPPENED  \u00b7  PINS 1\u201313",
           font=f_sec, fill=INK)
    map_x0, map_y0, map_w, map_h = M, bot_y + 20, 576, 168
    d.rectangle([map_x0, map_y0, map_x0 + map_w, map_y0 + map_h],
                fill=(233, 224, 196), outline=RULE, width=1)

    def ll2xy(lat, lon):
        mx = map_x0 + (lon + 180) / 360 * map_w
        my = map_y0 + (80 - lat) / 140 * map_h
        return mx, my

    for poly in CONTINENTS:
        pts = [ll2xy(lat, lon) for lon, lat in poly]
        d.polygon(pts, fill=(216, 199, 163), outline=(160, 140, 95))
    for n, (lat, lon) in enumerate(PINS, start=1):
        px, py = ll2xy(lat, lon)
        dx, dy = PIN_OFFSETS.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            d.line([(px, py), (px + dx, py + dy)], fill=(120, 110, 90), width=1)
            px, py = px + dx, py + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline="white", width=1)
        num = str(n)
        tw = d.textlength(num, font=font(SANS_B, 9))
        d.text((px - tw / 2, py - 6), num, font=font(SANS_B, 9), fill="white")

    # DATE CHECK box
    dc_x0 = map_x0 + map_w + 12
    dc_x1 = W - M
    d.rectangle([dc_x0, bot_y, dc_x1, map_y0 + map_h], outline=RED, width=2)
    d.text((dc_x0 + 8, bot_y + 6), "DATE CHECK \u2014 HELD BACK ON PURPOSE",
           font=f_dc_t, fill=RED)
    yy = bot_y + 28
    for date, item in DATE_CHECK:
        d.text((dc_x0 + 8, yy), date + "  ", font=font(SANS_B, 10), fill=RED)
        dw = d.textlength(date + "  ", font=font(SANS_B, 10))
        lines = wrap(d, item, f_dc, dc_x1 - dc_x0 - 16 - dw)
        for li, line in enumerate(lines[:2]):
            d.text((dc_x0 + 8 + (dw if li == 0 else 0), yy), line,
                   font=f_dc, fill=INK)
            yy += 13
        yy += 5
    d.text((dc_x0 + 8, yy + 2), "A story dated before today cannot win today.",
           font=font(SANS, 10), fill=GREY)
    assert yy + 18 <= map_y0 + map_h, "date check overflow"

    # ---- legend + footer ----
    leg = ("BADGES:  C  CONFIRMED (2+ outlets)     O  OFFICIAL     R  REPORTED     "
           "CL  CLAIM     OG  ONGOING")
    tw = d.textlength(leg, font=f_leg)
    d.text(((W - tw) / 2, 956), leg, font=f_leg, fill=GREY)
    d.line([(M, 974), (W - M, 974)], fill=INK, width=1)
    foot1 = ("All stories occurred or were first reported on 25 November 2026 (UTC). "
             "Illustrations are original drawings, not photographs.")
    tw = d.textlength(foot1, font=f_foot)
    d.text(((W - tw) / 2, 982), foot1, font=f_foot, fill=GREY)
    foot2 = "Compiled from wire and press reports  \u00b7  news-image-20261125"
    tw = d.textlength(foot2, font=f_foot)
    d.text(((W - tw) / 2, 998), foot2, font=f_foot, fill=GREY)

    total = len(BIG3) + len(CARDS10) + len(ALSO)
    print(f"stories: {total} (3 big + 10 cards + {len(ALSO)} also), "
          f"regions: {len(REGIONS)}")
    img.save(OUT, format="PNG", optimize=True)
    print(f"saved {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
