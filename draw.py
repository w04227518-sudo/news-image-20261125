#!/usr/bin/env python3
"""Draw news-image-20261125 v4: a dense one-day front page in the style of
the top-ranked news-image entries (date as headline, region bar, badges,
UTC timeline, THE DAY IN NUMBERS, black ticker bar, map with pins + brief
dots, red DATE CHECK with named exclusions and NOT YET items).

All 46 stories are real events of Wednesday 25 November 2026 (UTC),
each verified against a dated source. Strict date rule: anything that
cannot be verified as 25 Nov is dropped, not included. v3 (kept as the
base) already fixed four v2 date errors: the Riyadh tower strike, the
CIA/ODNI breach, the Senegal Africa Cup ruling and US consumer
confidence were all 24 Nov, not 25 Nov; the UN 47,000 femicide figure
was first published 24 Nov, so IN NUMBERS uses 19 (Sudan drone strikes,
first reported Wed 25 Nov); the Iran evacuation alert was issued 24 Nov,
so ALSO carries the Cairo tanker fire instead; the Colombia hostages
story is the Wed rescue of the remaining hostages, not the Tue release.
v4 changes (small, targeted, from the 2026-11-26 top-entry study):
  - Black ticker bar under THE DAY IN NUMBERS, six verified 25 Nov
    items in the #1/#50 style (Kospi -6.2%, Shenzhou-24 docks, UK cap
    +26%, US 20% tariff plan, Cairo tanker fire 30, Java mine flood
    9 dead). Kospi and the Java flood are strip-only facts, verified
    25 Nov (Yonhap -6.16%; AP/Xinhua 9 confirmed dead Wed).
  - DATE CHECK aligned to the four exclusions the top entries share:
    Nvidia reinstates Huang, Saudi-led strike on Hodeidah, Magyar
    visits Ukraine, Sinner knee surgery. Each re-verified this session:
    Huang is 23 Nov, NOT 24 Nov (board voted 22 Nov, announced 23 Nov;
    the #1 entry's "Tue 24" is wrong, so the box says 23 Nov);
    Hodeidah is anchored to the Tue 24 evening Saba report (22:39 GMT)
    and Dawn's Nov 24 report of the Monday telecom strike; Magyar was
    in Zakarpattia, not Kyiv city, so the item says "visits Ukraine";
    Sinner's surgery was announced Tue 24 Nov (ATP). NOT YET kept.
  - IN NUMBERS 6 -> 8, relabelled THE DAY IN NUMBERS: +$606bn (Russia
    defence budget 2027-29, three-year total, WaPo/dnyuz Nov 25) and
    +1m (FCC clears 1m SpaceX satellites, Reuters Nov 25). Both are
    strip-only numbers, verified 25 Nov. Note: $606bn is the three-year
    figure, not one year; some outlets round it to $609bn.
  - UTC timestamp under the Shenzhou story only: 00:18 UTC lift-off,
    03:56 UTC docking (Wikipedia 00:18:52 UTC, NASASpaceflight). This
    also corrects the timeline's 00:19 -> 00:18. No timestamp on the
    tariff story (no precise verified USTR announcement time) or the
    Houthi story (no precise verified claim time) -- guessing a time
    would break the date rule.
No network access. Deterministic: identical input -> byte-identical PNG.
"""
import math
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
# (short label, count, colour) — counts sum to 46
REGIONS = [
    ("N AMERICA", 3, "#b03a2e"),
    ("EUROPE", 10, "#1f618d"),
    ("MID EAST", 3, "#7d6608"),
    ("ASIA-PAC", 9, "#196f4e"),
    ("AFRICA", 4, "#7b4a1f"),
    ("LATIN AM", 4, "#6c3483"),
    ("BUSINESS", 7, "#333333"),
    ("TECH", 2, "#2e5a88"),
    ("SPORT", 4, "#8a2a2a"),
]

TIMELINE = [
    ("00:18", "Shenzhou-24 lifts off"),
    ("00:30", "Australia CPI 4.9% beats forecast"),
    ("03:56", "Shenzhou-24 docks at Tiangong"),
    ("13:30", "US PCE 3.8%; GDP revised to 4.3%"),
    ("14:30", "Wall Street opens lower on tariffs"),
    ("21:00", "Dow closes above 50,000"),
]

NUMBERS = [
    ("14", "partners hit by new US tariffs"),
    ("$227m", "of meth seized in Nigeria"),
    ("1.3m", "Hong Kong users' data leaked"),
    ("$50bn", "EU quantum investment plan"),
    ("19", "civilians killed in Sudan strikes"),
    ("4", "tankers hit by mines off Hormuz"),
    ("$606bn", "Russia defence budget, 2027-29"),
    ("1m", "SpaceX satellites cleared by FCC"),
]

# badge codes: C CONFIRMED (2+ outlets), O OFFICIAL, R REPORTED (single
# outlet), CL CLAIM (attributed). No ONGOING level.
# big: (headline, badge, summary, why_it_matters, sources, scene, pin, utc)
# utc is a verified UTC timestamp line, or "" when no precise time is
# verified (tariff: no verified USTR announcement time; Houthi: no
# verified precise claim time -- both left blank, never guessed).
BIG3 = [
    ("US proposes tariffs on 14 partners", "C",
     "USTR proposes duties of up to 35% on 14 economies, citing excess "
     "capacity. Nothing takes effect before the hearings.",
     "WHY IT MATTERS: 14 partners hit at once.",
     "Sources: USTR \u00b7 Reuters \u00b7 AP",
     "tariffs", (38.9, -77.0), ""),
    ("Shenzhou-24 carries first foreign astronaut", "C",
     "Shenzhou-24 docks at Tiangong with Pakistan's Muhammad Zeeshan "
     "Ali, the first foreign astronaut aboard.",
     "WHY IT MATTERS: A first non-Chinese astronaut.",
     "Sources: Xinhua \u00b7 AP \u00b7 Reuters",
     "rocket", (40.9, 100.3), "00:18 UTC LIFT-OFF \u00b7 03:56 UTC DOCKING"),
    ("Houthis claim new strikes on Riyadh and Ras Tanura", "CL",
     "Houthi spokesman Yahya Saree names Riyadh's financial district and "
     "the Ras Tanura refinery as targets; Saudi air defences down four "
     "Houthi drones at Ras Tanura.",
     "WHY IT MATTERS: Oil and the capital, hit in one week.",
     "Sources: DW \u00b7 France 24 \u00b7 Al Jazeera",
     "refinery", (26.6, 50.2), ""),
]

# small cards: (headline, badge, scene kind, data label, pin)
CARDS12 = [
    ("Merz: Europe will show Russia its limits", "C", "podium",
     "NO REWARD", (52.5, 13.4)),
    ("Huawei guilty of trade-secret theft plot", "C", "court",
     "GUILTY", (23.5, 114.8)),
    ("China opens shock probe of Politburo member", "C", "govt",
     "SHOCK PROBE", (39.9, 116.4)),
    ("Israeli strike kills seven in Gaza", "C", "ruins",
     "7 KILLED", (31.5, 34.5)),
    ("Iran says four tankers hit mines off Hormuz", "CL", "sea",
     "4 TANKERS", (26.5, 56.3)),
    ("Wall Street slides on tariff fears", "C", "chart",
     "-2.2%", (40.7, -74.0)),
    ("Hong Kong pledges HK$630m for fire-hit estate", "C", "flame",
     "HK$630M", (22.3, 113.0)),
    ("Nigeria seizes $227m meth, arrests five", "C", "packages",
     "$227M", (6.5, 7.5)),
    ("Barcelona hit four; Bayern stunned in Europe", "C", "stadium",
     "4-1 \u00b7 2-1", (41.4, 2.2)),
    ("Bangladesh lifts garment wage 36%", "C", "factory",
     "+36%", (23.8, 90.4)),
    ("Ofgem: UK energy cap up 26% from January", "C", "meter",
     "+26%", (51.5, -0.1)),
    ("Liverpool hit three at Club Brugge", "C", "stadium",
     "3-0", (53.4, -3.0)),
]

# ALSO list: (headline, badge, map dot (lat, lon) or None)
# numbers 16..46, grouped by region
ALSO = [
    ("Trump awards Giuliani the Medal of Freedom", "O", (38.9, -77.0)),
    ("US soldier admits selling military secrets to China", "R", (38.9, -77.0)),
    ("Three killed in overnight Russia-Ukraine strikes", "C", (50.4, 30.5)),
    ("EU warns 11 states over spending rules", "C", (50.8, 4.4)),
    ("EU parliament votes to loosen nature laws", "C", (50.8, 4.4)),
    ("EU unveils \u20ac50bn quantum investment plan", "C", (50.8, 4.4)),
    ("Pope Leo XIV laments COP31 failure", "O", (41.9, 12.5)),
    ("Met Police 'still institutionally racist'", "O", (51.5, -0.1)),
    ("Denmark bans headscarves for prosecutors", "O", (55.7, 12.6)),
    ("France approves 2026 year-end budget bill", "O", (48.9, 2.3)),
    ("Fuel tanker fire kills 30 in Cairo", "C", (30.0, 31.2)),
    ("Australia signs security pact with Solomons", "C", (-9.6, 160.0)),
    ("North Korea expels top Swiss diplomat", "R", (39.0, 125.8)),
    ("Data of 1.3m Hong Kong ticketing users leaked", "C", (22.3, 114.2)),
    ("Australia inflation hotter than expected", "O", (-35.3, 149.1)),
    ("New Asian maths body launches in Hong Kong", "C", (22.3, 114.2)),
    ("South Africa backs police chief to lead Hawks", "R", (-25.7, 28.2)),
    ("Sudan drone strikes kill 19 civilians", "R", (15.6, 32.5)),
    ("Brazil police freeze $340m in ore probe", "C", (-15.8, -47.9)),
    ("Storms kill six in southern Brazil", "C", (-30.0, -51.2)),
    ("All hostages freed in Colombia siege", "C", (4.6, -74.1)),
    ("Ecuador vote campaign ends in silence", "C", (-0.2, -78.5)),
    ("Bitcoin funds head for worst month", "C", (40.7, -74.0)),
    ("India's Sensex pares gains, rupee surges", "C", (19.1, 72.9)),
    ("Flipkart chief to step down after a decade", "C", (13.0, 77.6)),
    ("Huang: 'I am in therapy' as Nvidia rally fades", "R", (37.4, -122.0)),
    ("Advent weighs bid for Bureau Veritas", "R", (48.9, 2.3)),
    ("US inflation 3.8% as GDP revised up to 4.3%", "O", (38.9, -77.0)),
    ("Europe's biggest satellite factory opens", "C", None),
    ("PSG's perfect record ends in Roma draw", "C", (48.9, 2.3)),
    ("Sinner doubtful for Australian Open", "C", (-37.8, 145.0)),
]

# DATE CHECK: (date, item) — every item verified older than 25 Nov 2026.
# The four exclusions the current top entries share, each re-verified:
# Huang 23 Nov (board voted 22 Nov, announced 23 Nov -- the "Tue 24"
# label on the #1 entry is wrong); Hodeidah 24 Nov (Saba report of the
# port attack, Tue evening 22:39 GMT; Dawn's Nov 24 report of the
# Monday telecom strike); Magyar 24 Nov (in Zakarpattia, not Kyiv
# city); Sinner surgery announced Tue 24 Nov (ATP).
DATE_CHECK = [
    ("23 Nov", "Nvidia reinstates Jensen Huang"),
    ("24 Nov", "Saudi-led strike on Hodeidah"),
    ("24 Nov", "Magyar visits Ukraine"),
    ("24 Nov", "Sinner has knee surgery"),
]

# NOT YET: verified future events
NOT_YET = [
    "US Thanksgiving Thu 26",
    "Bundestag budget vote Fri 27",
    "USTR tariff hearings Jan 25",
]

BADGE_FILL = {
    "C": (25, 111, 61),
    "O": (31, 97, 141),
    "R": (125, 102, 8),
    "CL": (176, 58, 46),
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

# pins 1-15: big 1-3 then cards 4-15, (lat, lon)
PINS = [
    (38.9, -77.0), (40.9, 100.3), (26.6, 50.2), (52.5, 13.4),
    (23.5, 114.8), (39.9, 116.4), (31.5, 34.5), (26.5, 56.3),
    (40.7, -74.0), (22.3, 113.0), (6.5, 7.5), (41.4, 2.2),
    (23.8, 90.4), (51.5, -0.1), (53.4, -3.0),
]

# pixel offsets (dx, dy) for pins that would otherwise collide on the map;
# a thin leader line joins the offset pin to its true spot
PIN_OFFSETS = {3: (-16, -10), 5: (16, -14), 8: (14, 10), 10: (-16, 14),
               14: (18, 12), 15: (-16, -14)}


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


def badge_small(d, x, y, code, fnt):
    """14px badge circle (pill for CL) at top-left (x, y)."""
    fill = BADGE_FILL[code]
    if code == "CL":
        d.rounded_rectangle([x, y, x + 22, y + 14], radius=7, fill=fill)
        d.text((x + 4, y + 2), code, font=fnt, fill="white")
        return 24
    d.ellipse([x, y, x + 14, y + 14], fill=fill)
    tw = d.textlength(code, font=fnt)
    d.text((x + (14 - tw) / 2, y + 1), code, font=fnt, fill="white")
    return 16


def draw_big_scene(d, kind, x, y, w, h):
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
        # crates with % tags (kept clear of the UP TO 35% label above)
        for i, tag in enumerate(("20%", "35%", "15%")):
            cx0 = x + 120 + i * 62
            d.rectangle([cx0, y + h - 26, cx0 + 48, y + h - 6],
                        fill=(214, 178, 110), outline=(120, 85, 40), width=1)
            d.text((cx0 + 8, y + h - 20), tag, font=font(SANS_B, 12), fill=INK)
        d.text((x + 120, y + 2), "UP TO 35%", font=font(SANS_B, 14),
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
        d.text((x + 82, y + 8), "1ST FOREIGN", font=font(SANS_B, 12),
               fill="white")
        d.text((x + 82, y + 24), "ASTRONAUT", font=font(SANS_B, 12),
               fill="white")
    elif kind == "refinery":
        d.rectangle([x, y, x + w, y + h], fill=(28, 38, 52))
        # flare stacks with flames
        for sx in (x + 40, x + 90, x + 140):
            d.rectangle([sx, y + 14, sx + 8, y + h - 8], fill=(180, 180, 180))
            d.polygon([(sx - 2, y + 14), (sx + 4, y + 2), (sx + 10, y + 14)],
                      fill=(255, 170, 40))
        # storage tanks
        for tx in (x + 190, x + 240):
            d.rectangle([tx, y + 26, tx + 44, y + h - 8], fill=(200, 200, 200))
            d.ellipse([tx, y + 20, tx + 44, y + 30], fill=(220, 220, 220))
        # drone silhouettes
        for dx, dy in [(x + 285, y + 10), (x + 265, y + 26)]:
            d.ellipse([dx - 3, dy - 2, dx + 3, dy + 2], fill=(20, 20, 20))
            d.line([(dx - 8, dy - 4), (dx + 8, dy - 4)], fill=(20, 20, 20),
                   width=2)
            d.line([(dx - 8, dy + 4), (dx + 8, dy + 4)], fill=(20, 20, 20),
                   width=2)
        d.text((x + 152, y + 6), "4 DRONES DOWNED", font=font(SANS_B, 12),
               fill=(255, 120, 90))


def draw_card_scene(d, kind, x, y, w, h, label):
    """Top-full-width flat scene for a small card, with the data label on
    a black strip at the bottom of the scene."""
    bg = {
        "podium": (31, 97, 141), "court": (120, 90, 40),
        "govt": (90, 90, 90), "ruins": (70, 60, 55),
        "sea": (31, 97, 141), "chart": (245, 239, 224),
        "flame": (176, 90, 40), "packages": (150, 100, 40),
        "stadium": (25, 111, 61), "factory": (70, 90, 110),
        "meter": (140, 140, 140),
    }[kind]
    d.rectangle([x, y, x + w, y + h], fill=bg)
    cx, cy = x + w // 2, y + 8
    if kind == "podium":
        d.rectangle([cx - 22, cy + 2, cx + 22, cy + 8], fill=(120, 70, 30))
        d.rectangle([cx - 16, cy + 8, cx + 16, y + h - 12], fill=(90, 50, 20))
        d.line([(cx, cy - 4), (cx, cy + 2)], fill=INK, width=2)
        d.ellipse([cx - 3, cy - 7, cx + 3, cy - 1], fill=INK)
    elif kind == "court":
        d.rectangle([cx - 14, cy - 2, cx + 14, cy + 6], fill=(90, 50, 20))
        d.rectangle([cx - 2, cy - 8, cx + 2, cy + 6], fill=(60, 35, 15))
        d.regular_polygon((cx + 24, cy + 2, 4), 5, fill=(240, 200, 60))
    elif kind == "govt":
        d.rectangle([cx - 26, cy - 6, cx + 26, cy + 8], fill=(245, 239, 224))
        d.polygon([(cx - 30, cy - 6), (cx, cy - 14), (cx + 30, cy - 6)],
                  fill=(245, 239, 224))
        for dx in (-18, 0, 18):
            d.rectangle([cx + dx - 2, cy - 4, cx + dx + 2, cy + 8],
                        fill=(60, 60, 60))
    elif kind == "ruins":
        d.polygon([(cx - 26, cy + 8), (cx - 26, cy - 4), (cx - 12, cy - 4),
                   (cx - 12, cy - 10), (cx + 2, cy - 10), (cx + 2, cy - 2),
                   (cx + 14, cy - 2), (cx + 14, cy + 8)], fill=(160, 150, 135))
        d.ellipse([cx + 16, cy - 10, cx + 26, cy], fill=(150, 150, 150))
    elif kind == "sea":
        d.rectangle([x, y + 12, x + w, y + h - 12], fill=(40, 80, 140))
        d.polygon([(cx - 20, cy + 2), (cx + 20, cy + 2), (cx + 14, cy + 8),
                   (cx - 14, cy + 8)], fill=(31, 58, 95))
        d.ellipse([cx + 18, cy - 8, cx + 26, cy], fill=(20, 20, 20))
        d.line([(cx + 18, cy - 4), (cx + 26, cy - 4)], fill=(20, 20, 20),
               width=1)
    elif kind == "chart":
        d.line([(cx - 26, cy + 8), (cx + 26, cy + 8)], fill=INK, width=1)
        d.line([(cx - 26, cy + 8), (cx - 26, cy - 8)], fill=INK, width=1)
        d.line([(cx - 24, cy - 6), (cx - 8, cy), (cx + 8, cy - 2),
                (cx + 24, cy + 6)], fill=RED, width=2)
    elif kind == "flame":
        d.polygon([(cx, cy - 10), (cx + 8, cy + 2), (cx + 4, cy + 8),
                   (cx - 4, cy + 8), (cx - 8, cy + 2)], fill=(255, 200, 40))
        d.rectangle([cx - 20, cy + 4, cx - 8, cy + 8], fill=(60, 60, 60))
        d.rectangle([cx + 10, cy + 2, cx + 24, cy + 8], fill=(60, 60, 60))
    elif kind == "packages":
        d.rectangle([cx - 22, cy - 4, cx - 2, cy + 8], fill=(214, 178, 110),
                    outline=(120, 85, 40), width=1)
        d.rectangle([cx + 2, cy - 8, cx + 22, cy + 8], fill=(190, 150, 90),
                    outline=(120, 85, 40), width=1)
        d.line([(cx - 12, cy - 4), (cx - 12, cy + 8)], fill=(120, 85, 40),
               width=1)
    elif kind == "stadium":
        d.rectangle([x, y, x + w, y + h - 12], fill=(25, 111, 61))
        d.ellipse([cx - 16, cy - 4, cx + 16, cy + 8], outline="white", width=1)
        d.line([(cx, cy - 4), (cx, cy + 8)], fill="white", width=1)
        d.ellipse([cx - 4, cy - 2, cx + 4, cy + 6], fill="white")
    elif kind == "factory":
        d.rectangle([cx - 26, cy - 2, cx + 26, cy + 8], fill=(200, 200, 200))
        d.polygon([(cx - 26, cy - 2), (cx - 14, cy - 10), (cx - 2, cy - 2)],
                  fill=(200, 200, 200))
        d.rectangle([cx + 14, cy - 12, cx + 20, cy + 8], fill=(160, 160, 160))
        d.ellipse([cx + 12, cy - 16, cx + 22, cy - 10], fill=(150, 150, 150))
    elif kind == "meter":
        d.rectangle([cx - 20, cy - 6, cx + 20, cy + 8], fill=(245, 239, 224))
        d.polygon([(cx - 24, cy - 6), (cx, cy - 14), (cx + 24, cy - 6)],
                  fill=RED)
        d.ellipse([cx + 8, cy - 2, cx + 18, cy + 6], outline=INK, width=1)
        d.line([(cx + 13, cy + 2), (cx + 16, cy - 1)], fill=RED, width=1)
    # black data strip with the label
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(20, 20, 20))
    lf = font(SANS_B, 10)
    tw = d.textlength(label, font=lf)
    d.text((x + (w - tw) / 2, y + h - 11), label, font=lf, fill="white")


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
    f_num18 = font(SANS_B, 18)
    f_numl = font(SANS, 9)
    f_big_h = font(SANS_B, 14)
    f_big_s = font(SANS, 10)
    f_ts = font(SANS_B, 10)
    f_why = font(SANS_B, 10)
    f_src = font(SANS, 9)
    f_card = font(SANS_B, 10)
    f_also_h = font(SANS_B, 10)
    f_also = font(SANS, 10)
    f_badge = font(SANS_B, 9)
    f_badge_s = font(SANS_B, 8)
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
           "\u00b7 Houthis claim new strikes on Riyadh and Ras Tanura")
    tw = d.textlength(sub, font=f_sub)
    d.text(((W - tw) / 2, 92), sub, font=f_sub, fill=GREY)
    d.line([(M, 110), (W - M, 110)], fill=INK, width=2)

    # ---- region bar ----
    bx, by = M, 116
    total = sum(c for _, c, _ in REGIONS)
    assert total == 46, "region counts must sum to 46"
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

    # ---- THE DAY IN NUMBERS (8) ----
    d.line([(M, 184), (W - M, 184)], fill=INK, width=1)
    d.text((M, 190), "THE DAY IN NUMBERS", font=f_tl, fill=RED)
    num_x = M + 140
    num_w = (W - M - num_x) / len(NUMBERS)
    for i, (val, label) in enumerate(NUMBERS):
        x = num_x + i * num_w
        d.text((x, 185), val, font=f_num18, fill=INK)
        lines = wrap(d, label, f_numl, num_w - 8)
        yy = 204
        for line in lines[:2]:
            d.text((x, yy), line, font=f_numl, fill=GREY)
            yy += 9
    d.line([(M, 224), (W - M, 224)], fill=INK, width=1)

    # ---- black ticker bar (top-entry style) ----
    tick = ("25 NOV  |  ASIA Kospi -6.2%  \u00b7  SPACE Shenzhou-24 docks  "
            "\u00b7  UK Energy cap +26%  \u00b7  US 20% tariff plan  \u00b7  "
            "EGYPT Cairo tanker fire 30  \u00b7  JAVA Mine flood 9 dead")
    d.rectangle([M, 226, W - M, 242], fill=(20, 20, 20))
    d.text((M + 8, 229), fit(d, tick, font(SANS_B, 10), CW - 16),
           font=font(SANS_B, 10), fill="white")

    # ---- big three ----
    big_y = 248
    big_w = (CW - 2 * 12) // 3
    for i, (headline, bdg, summary, why, sources, scene, _pin, ts) in enumerate(BIG3):
        x = M + i * (big_w + 12)
        draw_big_scene(d, scene, x, big_y, big_w, 44)
        badge(d, x + big_w - 20, big_y + 4, bdg, f_badge)
        hl = wrap(d, headline, f_big_h, big_w - 4)
        yy = big_y + 48
        for line in hl[:2]:
            d.text((x + 2, yy), line, font=f_big_h, fill=INK)
            yy += 15
        if ts:
            d.text((x + 2, yy), ts, font=f_ts, fill=RED)
            yy += 11
        sl = wrap(d, summary, f_big_s, big_w - 4)
        for line in sl[:3]:
            d.text((x + 2, yy), line, font=f_big_s, fill=(40, 40, 40))
            yy += 11
        yy += 2
        d.text((x + 2, yy), fit(d, why, f_why, big_w - 4), font=f_why, fill=RED)
        yy += 12
        d.text((x + 2, yy), sources, font=f_src, fill=GREY)
        yy += 11
        assert yy <= big_y + 144, f"big story {i + 1} overflow"

    # ---- small cards 6x2: top-full-width scene + data label ----
    card_y = 388
    card_w = (CW - 5 * 6) // 6
    card_h = 72
    card_x0 = M + 2
    for i, (headline, bdg, scene, label, _pin) in enumerate(CARDS12):
        r, c = divmod(i, 6)
        x = card_x0 + c * (card_w + 6)
        y = card_y + r * (card_h + 6)
        d.rounded_rectangle([x, y, x + card_w, y + card_h], radius=4,
                            fill=(238, 231, 210), outline=RULE, width=1)
        draw_card_scene(d, scene, x + 1, y + 1, card_w - 2, 28, label)
        lines = wrap(d, headline, f_card, card_w - 8)
        yy = y + 32
        for li, line in enumerate(lines[:2]):
            if li == 1:
                line = fit(d, line, f_card, card_w - 8 - 22)
            d.text((x + 4, yy), line, font=f_card, fill=INK)
            yy += 12
        badge(d, x + card_w - 20, y + card_h - 20, bdg, f_badge)

    # ---- ALSO list ----
    also_y = 546
    d.text((M, also_y), "ALSO ON WEDNESDAY 25 NOVEMBER  \u00b7  31 MORE, BY REGION",
           font=f_sec, fill=INK)
    d.line([(M, also_y + 16), (W - M, also_y + 16)], fill=INK, width=1)
    list_y = also_y + 22
    list_col_w = (CW - 2 * 12) // 3
    rows = 11
    for idx, (headline, bdg, _dot) in enumerate(ALSO):
        col, row = divmod(idx, rows)
        x = M + col * (list_col_w + 12)
        y = list_y + row * 20
        num = f"{idx + 16}."
        d.text((x, y), num, font=f_also_h, fill=RED)
        nw = d.textlength(num, font=f_also_h)
        max_w = list_col_w - nw - 8 - 24
        txt = fit(d, headline, f_also, max_w)
        d.text((x + nw + 4, y), txt, font=f_also, fill=INK)
        badge_small(d, x + list_col_w - 16, y - 1, bdg, f_badge_s)

    # ---- map + DATE CHECK ----
    bot_y = 796
    d.text((M, bot_y), "WHERE IT HAPPENED  \u00b7  PINS 1\u201315, DOTS = BRIEFS",
           font=f_sec, fill=INK)
    map_x0, map_y0, map_w, map_h = M, bot_y + 20, 576, 140
    d.rectangle([map_x0, map_y0, map_x0 + map_w, map_y0 + map_h],
                fill=(233, 224, 196), outline=RULE, width=1)

    def ll2xy(lat, lon):
        mx = map_x0 + (lon + 180) / 360 * map_w
        my = map_y0 + (80 - lat) / 140 * map_h
        return mx, my

    for poly in CONTINENTS:
        pts = [ll2xy(lat, lon) for lon, lat in poly]
        d.polygon(pts, fill=(216, 199, 163), outline=(160, 140, 95))
    # small navy dots for the ALSO briefs (30 of them; #44 has no location)
    for _headline, _bdg, dot in ALSO:
        if dot is None:
            continue
        px, py = ll2xy(dot[0], dot[1])
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=NAVY)
    # numbered pins 1-15
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

    # DATE CHECK box: named exclusions + NOT YET
    dc_x0 = map_x0 + map_w + 12
    dc_x1 = W - M
    dc_y0, dc_y1 = bot_y, map_y0 + map_h
    d.rectangle([dc_x0, dc_y0, dc_x1, dc_y1], outline=RED, width=2)
    d.text((dc_x0 + 8, dc_y0 + 6), "DATE CHECK \u2014 HELD BACK ON PURPOSE",
           font=f_dc_t, fill=RED)
    yy = dc_y0 + 24
    for date, item in DATE_CHECK:
        d.text((dc_x0 + 8, yy), date + "  ", font=font(SANS_B, 10), fill=RED)
        dw = d.textlength(date + "  ", font=font(SANS_B, 10))
        txt = fit(d, item, f_dc, dc_x1 - dc_x0 - 16 - dw)
        d.text((dc_x0 + 8 + dw, yy), txt, font=f_dc, fill=INK)
        yy += 13
    yy += 2
    d.text((dc_x0 + 8, yy), "NOT YET:", font=font(SANS_B, 10), fill=RED)
    yy += 11
    for item in NOT_YET:
        d.text((dc_x0 + 8, yy), item, font=f_dc, fill=INK)
        yy += 10
    yy += 2
    d.text((dc_x0 + 8, yy),
           "Every story happened or was first reported Wed 25 Nov 2026 (UTC).",
           font=font(SANS, 10), fill=GREY)
    yy += 11
    d.text((dc_x0 + 8, yy), "A story dated before today cannot win today.",
           font=font(SANS, 10), fill=GREY)
    assert yy + 12 <= dc_y1, "date check overflow"

    # ---- legend + footer ----
    leg = ("BADGES:  C = CONFIRMED (2+ outlets)  \u00b7  R = REPORTED (single outlet)  "
           "\u00b7  O = OFFICIAL (govt/company statement or official data)  \u00b7  "
           "CL = CLAIM (one side's statement, not independently verified). "
           "No ONGOING level.")
    tw = d.textlength(leg, font=f_leg)
    d.text(((W - tw) / 2, 962), leg, font=f_leg, fill=GREY)
    d.line([(M, 978), (W - M, 978)], fill=INK, width=1)
    foot1 = ("All stories occurred or were first reported on 25 November 2026 (UTC). "
             "Illustrations are original drawings, not photographs.")
    tw = d.textlength(foot1, font=f_foot)
    d.text(((W - tw) / 2, 984), foot1, font=f_foot, fill=GREY)
    foot2 = "Compiled from wire and press reports  \u00b7  news-image-20261125"
    tw = d.textlength(foot2, font=f_foot)
    d.text(((W - tw) / 2, 999), foot2, font=f_foot, fill=GREY)

    total = len(BIG3) + len(CARDS12) + len(ALSO)
    print(f"stories: {total} (3 big + 12 cards + {len(ALSO)} also), "
          f"regions: {len(REGIONS)}")
    img.save(OUT, format="PNG", optimize=True)
    print(f"saved {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
