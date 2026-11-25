#!/usr/bin/env python3
"""Render the make.fun news-image-20261125 magazine entry (1024x1024).

Fresh build for the 25 November 2026 bounty. Magazine concept, revised
per the user's direction: the masthead is the date itself
('WEDNESDAY 25 NOVEMBER 2026') in a Vogue-style Didone serif
(Playfair Display), with the cover title 'THE BURNING SEA' below it
on the cream page background — no red masthead band, no dateline
strip, no headline overlaid on the cover photo. 8 feature tiles
with photos, and an ALSO ON TODAY list with all 16 remaining stories.
All photos are Wikimedia Commons, credited in README.md.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(HERE, "photos")

# Palette: bright magazine red / yellow / blue on cream paper.
# (Red is kept only as a small accent — headlines, bullets, footer —
# never as a header background.)
RED = (210, 31, 43)
YELLOW = (255, 196, 0)
BLUE = (11, 61, 145)
CREAM = (251, 246, 236)
INK = (17, 17, 17)
GREY = (70, 70, 70)
WHITE = (255, 255, 255)
LIGHT = (238, 231, 218)

FONT_DIR = "/usr/share/fonts/truetype/noto"
BLACK = os.path.join(FONT_DIR, "NotoSans-Black.ttf")
BOLD = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")
ITAL = os.path.join(FONT_DIR, "NotoSans-Italic.ttf")
# Vogue-style Didone serif (Playfair Display, OFL) for date + title.
DIDONE = os.path.join(HERE, "fonts", "PlayfairDisplay.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def didone(size, weight="Bold"):
    """Playfair Display at the named variable-font weight."""
    fnt = ImageFont.truetype(DIDONE, size)
    try:
        fnt.set_variation_by_name(weight)
    except Exception:
        pass
    return fnt


def fit_font(draw, text, make, size, max_w, min_size=20):
    """Shrink a font until text fits max_w; returns (font, size)."""
    while size > min_size:
        fnt = make(size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt, size
        size -= 2
    return make(min_size), min_size


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
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


def cover_crop(img, tw, th, focus="center"):
    """Crop an image to fill tw x th. focus: center/top/bottom (vertical)."""
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    if focus == "top":
        y = 0
    elif focus == "bottom":
        y = nh - th
    else:
        y = (nh - th) // 2
    return img.crop((x, y, x + tw, y + th))


def paste_photo(base, path, box, bright=1.0, focus="center"):
    img = Image.open(path).convert("RGB")
    img = cover_crop(img, box[2] - box[0], box[3] - box[1], focus)
    if bright != 1.0:
        img = ImageEnhance.Brightness(img).enhance(bright)
    base.paste(img, (box[0], box[1]))
    # thin dark frame
    d = ImageDraw.Draw(base)
    d.rectangle(box, outline=(0, 0, 0), width=1)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- Masthead: the date itself, Vogue-style Didone serif ------------
    # No coloured band — the date sits on the cream page background.
    f_date, _ = fit_font(d, "WEDNESDAY 25 NOVEMBER 2026",
                         lambda s: didone(s, "Bold"), 52, 980)
    d.text((W // 2, 40), "WEDNESDAY 25 NOVEMBER 2026", font=f_date,
           fill=INK, anchor="mm")

    # ---- Cover title below the date --------------------------------------
    f_title, _ = fit_font(d, "THE BURNING SEA",
                          lambda s: didone(s, "Bold"), 72, 960)
    d.text((W // 2, 100), "THE BURNING SEA", font=f_title,
           fill=INK, anchor="mm")
    f_titsub = font(BOLD, 19)
    d.text((W // 2, 144), "Ukraine's drone war spreads to two more seas",
           font=f_titsub, fill=INK, anchor="mm")
    # thin hairline rule, Vogue-style
    d.line([(28, 164), (W - 28, 164)], fill=(60, 60, 60), width=2)

    # ---- Cover photo (clean — no headline overlaid on it) ----------------
    paste_photo(img, os.path.join(PHOTOS, "cover.jpg"), (0, 176, W, 396))
    d = ImageDraw.Draw(img)

    # ---- Cover deck ------------------------------------------------------
    f_deck = font(REG, 18)
    deck = ("A Russian warship sunk off Libya, a cargo ship hit in the Gulf of Finland, "
            "a container ship targeted near Hormuz.")
    lines = wrap(d, deck, f_deck, W - 28)
    y = 406
    for ln in lines:
        d.text((14, y), ln, font=f_deck, fill=INK)
        y += 22
    f_note = font(ITAL, 13)
    d.text((14, 454), "Strikes on 21–22 Nov, confirmed 23 Nov — the fallout continues today.",
           font=f_note, fill=GREY)

    # ---- Features header -------------------------------------------------
    d.rectangle([0, 476, W, 500], fill=BLUE)
    f_sec = font(BOLD, 17)
    d.text((14, 488), "TODAY'S BIG STORIES", font=f_sec, fill=WHITE, anchor="lm")

    # ---- 8 feature tiles -------------------------------------------------
    features = [
        ("f1_huawei.jpg", "HUAWEI GUILTY",
         "Guilty on 10 of 12 counts: Iran business, bank fraud, trade-secret theft.", "top"),
        ("f2_cia.jpg", "CIA HACKED",
         "Hackers breach the spies' open-source network; no classified data hit.", "center"),
        ("f3_tokyo.jpg", "ASIA SELLS OFF",
         "Kospi −5.3%, Taiwan −5.1%, Nikkei −2.9% as fresh US tariff threats hit.", "center"),
        ("f4_tanker.jpg", "HORMUZ BURNS TOO",
         "Ship targeted near the Strait; Brent falls to ~$91 as glut fears beat war fears.", "center"),
        ("f5_bitcoin.jpg", "BITCOIN UNDER $60,000",
         "$59,089 and sliding — but not a new low; the $55,130 trough was 21 Nov.", "center"),
        ("f6_nyse.jpg", "WALL ST SPLITS",
         "Nasdaq −1.5%, S&P −0.5%, Dow +0.9%. Nvidia's bounce fades, −5.9%.", "center"),
        ("f7_gaza.jpg", "GAZA GROUND PUSH",
         "Israel's first broad ground offensive in central Gaza since the 2025 ceasefire.", "center"),
        ("f8_ebola.jpg", "EBOLA TEAM RESCUED",
         "WHO staff evacuated from a Congo hospital after three days of fighting.", "center"),
    ]
    tile_w, tile_h, gap = 244, 110, 12
    x0, y0 = 6, 508
    f_th = font(BOLD, 15)
    f_td = font(REG, 12)
    for i, (photo, head, desc, focus) in enumerate(features):
        col, row = i % 4, i // 4
        x = x0 + col * (tile_w + gap)
        yy = y0 + row * (tile_h + gap)
        paste_photo(img, os.path.join(PHOTOS, photo), (x, yy, x + tile_w, yy + 52),
                    focus=focus)
        d = ImageDraw.Draw(img)
        # headline: one line, shrink if needed
        hs = 15
        while d.textlength(head, font=font(BOLD, hs)) > tile_w and hs > 11:
            hs -= 1
        d.text((x, yy + 56), head, font=font(BOLD, hs), fill=RED)
        dlines = wrap(d, desc, f_td, tile_w)
        dy = yy + 56 + hs + 3
        for ln in dlines[:2]:
            d.text((x, dy), ln, font=f_td, fill=INK)
            dy += 15

    # ---- ALSO ON header --------------------------------------------------
    d.rectangle([0, 746, W, 770], fill=BLUE)
    d.text((14, 758), "ALSO ON TODAY", font=f_sec, fill=WHITE, anchor="lm")

    # ---- ALSO ON list: 16 items, 2 columns x 8 rows ---------------------
    also = [
        ("Trump tariff probe findings due", "USTR Section 301 findings on 16 partners expected; new duties to follow."),
        ("China probes Politburo member", "Shanghai chief Chen Jining investigated, the fourth since 2025."),
        ("India defies the sell-off", "Sensex +1,497 to 83,933; rupee 92.62; record $13.2bn inflows in Nov."),
        ("Indonesia mine rescue", "Rescuers search for dozens trapped 100m deep in a flooded gold mine in Bogor."),
        ("FinCEN breached too", "Treasury's crime-fighting unit hit in a separate incident on Tuesday."),
        ("Gold slides; Fed hike nearly certain", "Gold $3,544.54; markets price a ~97% chance of a December hike."),
        ("US data wall on Thanksgiving eve", "Core PCE and Q3 GDP land today; GDP expected +3.5% annualised."),
        ("Australia inflation runs hot", "Trimmed mean 3.8%, well above target; pressure builds on the Reserve Bank."),
        ("Russia extradites $2.3bn suspect", "Chinese national sent home over 15bn yuan in illegal deposits."),
        ("Citi eyes Venezuela return", "Bank weighs resuming business five years after exiting."),
        ("US consumer confidence jumps", "Index 103.3, highest in nearly two years, on post-midterm optimism."),
        ("OPEC+ meets 29 Nov", "Ministers to decide 2027 output; UAE no longer restricted."),
        ("Japan service prices hit 36-year high", "Yen steady at 159.28 per dollar."),
        ("US court blocks Pentagon discharges", "Appeals court halts discharge of 27 transgender service members."),
        ("NSA outage was not an attack", "Last week's classified network outage was software patching, officials say."),
        ("Anthropic sinks below IPO price", "Shares −6.54% to $81.90, under the $83 IPO price, as AI stocks sell off."),
    ]
    f_at = font(BOLD, 13)
    f_ad = font(REG, 11)
    col_w = (W - 24 - 20) // 2
    row_h = 27
    for i, (title, desc) in enumerate(also):
        col, row = i % 2, i // 2
        x = 12 + col * (col_w + 20)
        yy = 778 + row * row_h
        # red bullet square
        d.rectangle([x, yy + 3, x + 7, yy + 10], fill=RED)
        d.text((x + 12, yy), title, font=f_at, fill=INK)
        dlines = wrap(d, desc, f_ad, col_w - 12)
        d.text((x + 12, yy + 14), dlines[0] if dlines else "", font=f_ad, fill=GREY)

    # ---- Footer ----------------------------------------------------------
    d.rectangle([0, 1000, W, H], fill=RED)
    f_ft = font(REG, 12)
    d.text((W // 2, 1012),
           "Photos: Wikimedia Commons (credits in README)  ·  Stories verified against Reuters, AP, BBC  ·  25 November 2026",
           font=f_ft, fill=WHITE, anchor="mm")

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
