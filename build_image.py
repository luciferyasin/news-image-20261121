#!/usr/bin/env python3
"""Build the 21 Nov 2026 'THE WORLD TODAY' news image (1024x1024).

Layout system: white page, red masthead, bold date line, red rule,
one dominant hero photograph with a bottom scrim (location pill,
headline, one-line dek), a three-column story strip, an ALSO TODAY
briefs block and a credits footer. All photographs are real news
photographs published with 20-21 Nov 2026 coverage.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(HERE, "real_photos")
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

RED = (181, 18, 27)
INK = (17, 17, 17)
GREY = (110, 110, 110)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/noto"
F_BLACK = os.path.join(FONT_DIR, "NotoSans-Black.ttf")
F_XBOLD = os.path.join(FONT_DIR, "NotoSans-ExtraBold.ttf")
F_BOLD = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
F_SEMI = os.path.join(FONT_DIR, "NotoSans-SemiBold.ttf")
F_REG = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_crop(img, tw, th, fx=0.5, fy=0.5):
    """Resize+centre-crop img to exactly (tw, th), focus at (fx, fy)."""
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - tw) * fx)
    y = int((nh - th) * fy)
    x = max(0, min(x, nw - tw))
    y = max(0, min(y, nh - th))
    return img.crop((x, y, x + tw, y + th))


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def add_scrim(base, x, y, w, h, top_alpha=0, bot_alpha=205):
    """Vertical black gradient over the bottom part of the hero."""
    grad = Image.new("L", (1, h))
    for i in range(h):
        t = i / max(h - 1, 1)
        grad.putpixel((0, i), int(top_alpha + (bot_alpha - top_alpha) * t))
    grad = grad.resize((w, h))
    black = Image.new("RGB", (w, h), (0, 0, 0))
    base.paste(black, (x, y), grad)


def main():
    page = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(page)

    # ---- Masthead -------------------------------------------------
    mast = "T H E   W O R L D   T O D A Y"
    f_mast = font(F_BLACK, 57)
    mw = d.textlength(mast, font=f_mast)
    d.text(((W - mw) / 2, 18), mast, font=f_mast, fill=RED)

    f_date = font(F_BOLD, 27)
    date_line = "SATURDAY, 21 NOVEMBER 2026"
    dw = d.textlength(date_line, font=f_date)
    d.text(((W - dw) / 2, 84), date_line, font=f_date, fill=INK)

    d.rectangle([MARGIN, 122, W - MARGIN, 127], fill=RED)

    # ---- Hero -----------------------------------------------------
    hx, hy, hw, hh = MARGIN, 136, CONTENT_W, 548
    hero = fit_crop(Image.open(os.path.join(PHOTOS, "poland_mi24.jpg")).convert("RGB"),
                    hw, hh, fx=0.5, fy=0.42)
    page.paste(hero, (hx, hy))
    add_scrim(page, hx, hy + hh - 252, hw, 252)
    d = ImageDraw.Draw(page)

    pill_text = "NOWY LIPOWIEC, POLAND"
    f_pill = font(F_BOLD, 19)
    pw = d.textlength(pill_text, font=f_pill) + 26
    py = hy + hh - 238
    d.rectangle([hx + 22, py, hx + 22 + pw, py + 32], fill=RED)
    d.text((hx + 35, py + 5), pill_text, font=f_pill, fill=WHITE)

    f_head = font(F_XBOLD, 43)
    head_lines = wrap(d, "Russian missiles land in Poland as NATO chief heads to Warsaw",
                      f_head, hw - 44)
    ly = py + 44
    for ln in head_lines:
        d.text((hx + 22, ly), ln, font=f_head, fill=WHITE)
        ly += 50

    f_dek = font(F_REG, 22)
    dek_lines = wrap(d, "Two missiles and a jet-powered drone came down near allied "
                        "exercises; Warsaw calls it a deliberate provocation.",
                     f_dek, hw - 44)
    for ln in dek_lines:
        d.text((hx + 22, ly + 4), ln, font=f_dek, fill=(232, 232, 232))
        ly += 29

    # ---- Story strip ----------------------------------------------
    stories = [
        ("kryvyi_rih.jpg", 0.5, 0.40, "UKRAINE",
         "Kryvyi Rih strike: child, medic killed, 42 hurt"),
        ("riemann.jpg", 0.5, 0.45, "SCIENCE",
         "AI-assisted Riemann proof passes first checks"),
        ("gta_launch.jpg", 0.55, 0.45, "ENTERTAINMENT",
         "GTA VI makes $3.79bn in a day, a launch record"),
    ]
    col_w, gap = 306, 17
    sy = hy + hh + 14
    photo_h = 120
    f_tag = font(F_BOLD, 19)
    f_story = font(F_BOLD, 23)
    for i, (fname, fx, fy, tag, headline) in enumerate(stories):
        cx = MARGIN + i * (col_w + gap)
        img = fit_crop(Image.open(os.path.join(PHOTOS, fname)).convert("RGB"),
                       col_w, photo_h, fx=fx, fy=fy)
        page.paste(img, (cx, sy))
        d.text((cx, sy + photo_h + 8), tag, font=f_tag, fill=RED)
        lines = wrap(d, headline, f_story, col_w)
        ty = sy + photo_h + 36
        for ln in lines[:3]:
            d.text((cx, ty), ln, font=f_story, fill=INK)
            ty += 28

    # ---- Also today -----------------------------------------------
    by = 922
    d.line([MARGIN, by, W - MARGIN, by], fill=(200, 200, 200), width=1)
    f_brief = font(F_REG, 18)
    f_brief_b = font(F_BOLD, 18)
    briefs = ("Saudi air defences destroy three Houthi ballistic missiles over Riyadh "
              "\u00b7 FBI says hackers breached its national crime database "
              "\u00b7 Zelenskyy and US negotiators join coalition talks in Berlin")
    label = "ALSO TODAY   "
    lw = d.textlength(label, font=f_brief_b)
    d.text((MARGIN, by + 8), label, font=f_brief_b, fill=RED)
    blines = wrap(d, briefs, f_brief, CONTENT_W - lw)
    for j, ln in enumerate(blines[:2]):
        d.text((MARGIN + lw, by + 8 + j * 24), ln, font=f_brief, fill=INK)

    # ---- Footer ----------------------------------------------------
    f_foot = font(F_REG, 14)
    foot = ("Photos: PAP / Wojtek Jargi\u0142o \u00b7 Dnipropetrovsk OVA via Kyiv Independent "
            "\u00b7 Nature \u00b7 AP      Reporting: Reuters \u00b7 AP \u00b7 AFP \u00b7 Nature")
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 986), foot, font=f_foot, fill=GREY)

    page.save(OUT, format="JPEG", quality=90)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
