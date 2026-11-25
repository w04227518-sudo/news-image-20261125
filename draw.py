#!/usr/bin/env python3
"""Draw news-image-20261125 v1: a dense newspaper front page summarising
the world's news of Wednesday 25 November 2026. No network access.
Deterministic: identical input -> byte-identical PNG."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

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

# (section, [(headline, summary), ...])
SECTIONS = [
    ("NORTH AMERICA", [
        ("US proposes tariffs on 14 partners",
         "Headline rates of 20-40%; the EU faces 15% on top of existing duties. Hearing set for 25 January."),
        ("Wall Street slides on tariff fears",
         "S&P 500 falls about 2.2% and Nasdaq about 3.2% as AI, inflation and tariff worries bite."),
        ("CIA and spy chief hit by cyber breach",
         "Hackers accessed some unclassified information at the CIA and the ODNI, reports say."),
        ("US consumer confidence jumps",
         "Confidence soars as petrol prices fall; 81.5 million Americans set to travel for Thanksgiving."),
    ]),
    ("EUROPE", [
        ("Merz: Europe will show Russia its limits",
         "German chancellor defends a sharp rise in defence spending in the final budget debate."),
        ("Three killed in overnight Russia-Ukraine strikes",
         "Attacks hit Kyiv, Kharkiv, Zaporizhzhia and Samara; 15 people reported injured."),
        ("EU warns 11 states over spending rules",
         "Commission seeks tougher deficit action against Bulgaria and Hungary in 2027 budgets."),
        ("EU parliament votes to loosen nature laws",
         "MEPs vote 367-268 to review the Birds and Habitats Directives in a centre-right win."),
        ("EU unveils 50bn euro quantum investment plan",
         "Commission also proposes a 50bn euro fund to take stakes in European tech firms."),
    ]),
    ("MIDDLE EAST", [
        ("US tells citizens to leave Iran",
         "Washington warns hostilities could escalate fast as regional attacks stack up."),
        ("Iran says four tankers hit mines off Hormuz",
         "Tehran reports tankers struck naval mines and caught fire; the claims are unverified."),
        ("Riyadh skyscraper struck for second time",
         "Saudi capital's tallest tower hit again in days; at least 11 people injured."),
        ("Houthis claim strike on Saudi refinery",
         "Rebels say they set fire to the Ras Tanura refinery; the coalition says it downed four drones."),
    ]),
    ("ASIA-PACIFIC", [
        ("China launches Shenzhou-24 with first foreign astronaut",
         "Pakistan's Muhammad Zeeshan Ali joins two Chinese crew heading for the Tiangong station."),
        ("Huawei guilty of trade-secret theft plot",
         "US jury finds the Chinese tech giant conspired to steal trade secrets."),
        ("China opens shock probe into Politburo member",
         "Beijing announces a corruption investigation into a top-ranking party figure."),
        ("Australia signs security pact with Solomons",
         "Canberra becomes the archipelago's preferred defence partner in a deal signed on 25 November."),
        ("North Korea expels top Swiss diplomat",
         "Pyongyang accuses the envoy of a 'hostile act' amid a row over sanctions on a youth camp."),
        ("Hong Kong pledges HK$630m for fire-hit estate",
         "Support package for Wang Fuk Court residents as power tariffs rise 7.9% and 1.8%."),
        ("Data of 1.3m Hong Kong ticketing users leaked",
         "URBTIX user data compromised in a cyberattack, officials confirm."),
    ]),
    ("AFRICA", [
        ("Nigeria seizes $227m of meth, arrests five Mexicans",
         "Anti-drug agency makes the haul in Enugu state, warning of cartels using Nigeria as a base."),
        ("Africa Cup title handed back to Senegal",
         "CAS rules against Morocco, reversing the result of the continental final."),
        ("South Africa backs police chief to lead Hawks",
         "Cabinet agrees Nhlanhla Mkhwanazi will head the elite crime-fighting unit."),
    ]),
    ("LATIN AMERICA", [
        ("Brazil police freeze $340m in ore probe",
         "Operation Hubris targets illegal iron-ore mining in Minas Gerais."),
        ("Storms kill six in southern Brazil",
         "About 10,000 people affected across more than 40 towns in Parana state."),
        ("Gunmen free 10 hostages in Colombia",
         "Armed men release hostages after a stand-off at a supermarket in Cartagena."),
        ("Ecuador vote campaign ends in silence",
         "Local election campaigning closes; a 72-hour alcohol ban and fines follow before Sunday's vote."),
    ]),
    ("BUSINESS & MARKETS", [
        ("Bitcoin funds head for worst month",
         "Outflows near $5bn in November as crypto funds bleed."),
        ("India's Sensex pares gains, rupee surges",
         "Sensex falls 800 points from its high but still ends up 1%; rupee strengthens to 92.41."),
        ("Flipkart chief to step down after a decade",
         "Kalyan Krishnamurthy leaves the Walmart-owned e-commerce giant after a 10-year CEO run."),
    ]),
    ("TECHNOLOGY & SCIENCE", [
        ("New Asian maths body launches in Hong Kong",
         "Asian Mathematical Union, the first of its kind in the region, opens with a Tsinghua professor at its head."),
        ("Europe's biggest satellite factory opens",
         "Belgium's Aerospacelab inaugurates a 20,000 sq m Megafactory in Marcinelle."),
    ]),
    ("SPORT & CULTURE", [
        ("Barcelona hit four; Bayern stunned in Europe",
         "Champions League: Barca beat Sabah 4-1, Lille upset Bayern 2-1, PSG held 2-2 by Roma, Liverpool win 3-0."),
        ("Sinner doubtful for Australian Open",
         "The world No. 1 faces a race to be fit after knee surgery."),
    ]),
]

COLUMNS = [
    ["NORTH AMERICA", "EUROPE", "TECHNOLOGY & SCIENCE"],
    ["MIDDLE EAST", "ASIA-PACIFIC"],
    ["AFRICA", "LATIN AMERICA", "BUSINESS & MARKETS", "SPORT & CULTURE"],
]

def main():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    black = (0, 0, 0)
    grey = (90, 90, 90)
    light = (200, 200, 200)

    f_mast = font(SERIF_B, 62)
    f_date = font(SANS_B, 25)
    f_sub = font(SANS, 13)
    f_sec = font(SANS_B, 13)
    f_head = font(SANS_B, 13)
    f_sum = font(SANS, 11)
    f_foot = font(SANS, 10)

    # outer frame
    d.rectangle([5, 5, W - 6, H - 6], outline=black, width=3)

    # masthead
    title = "THE WORLD IN A DAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 22), title, font=f_mast, fill=black)
    d.line([(24, 100), (W - 24, 100)], fill=black, width=2)

    date = "WEDNESDAY 25 NOVEMBER 2026"
    tw = d.textlength(date, font=f_date)
    d.text(((W - tw) / 2, 110), date, font=f_date, fill=black)
    sub = "34 STORIES  •  ONE DAY  •  ALL THE NEWS THAT MATTERS"
    tw = d.textlength(sub, font=f_sub)
    d.text(((W - tw) / 2, 142), sub, font=f_sub, fill=grey)
    d.line([(24, 166), (W - 24, 166)], fill=black, width=2)

    sec_map = dict(SECTIONS)
    margin = 24
    gutter = 16
    col_w = (W - 2 * margin - 2 * gutter) // 3
    top = 178
    bottom = 986
    head_lh, sum_lh = 16, 13

    for ci, col_secs in enumerate(COLUMNS):
        x = margin + ci * (col_w + gutter)
        y = top
        for si, sec in enumerate(col_secs):
            # section header bar
            d.rectangle([x, y, x + col_w, y + 22], fill=black)
            d.text((x + 6, y + 4), sec, font=f_sec, fill="white")
            y += 22 + 6
            for headline, summary in sec_map[sec]:
                hl = wrap(d, headline, f_head, col_w - 4)
                sl = wrap(d, summary, f_sum, col_w - 4)
                hl = hl[:2]
                sl = sl[:2]
                for line in hl:
                    d.text((x + 2, y), line, font=f_head, fill=black)
                    y += head_lh
                for line in sl:
                    d.text((x + 2, y), line, font=f_sum, fill=(40, 40, 40))
                    y += sum_lh
                y += 5
                d.line([(x, y), (x + col_w, y)], fill=light, width=1)
                y += 6
            if si < len(col_secs) - 1:
                y += 4
        print(f"column {ci + 1} ends at y={y} (limit {bottom})")
        assert y <= bottom, f"column {ci + 1} overflows: {y} > {bottom}"

    # footer
    d.line([(24, 992), (W - 24, 992)], fill=black, width=1)
    foot = "News of Wednesday 25 November 2026  •  Compiled from wire and press reports  •  news-image-20261125"
    tw = d.textlength(foot, font=f_foot)
    d.text(((W - tw) / 2, 1000), foot, font=f_foot, fill=grey)

    total = sum(len(v) for _, v in SECTIONS)
    print(f"stories: {total}, sections: {len(SECTIONS)}")
    img.save(OUT, format="PNG", optimize=True)
    print(f"saved {OUT} ({os.path.getsize(OUT)} bytes)")

if __name__ == "__main__":
    main()
