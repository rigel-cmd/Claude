"""Visuels de la version contrastée de l'offre d'emploi (charte Victimes & Préjudices Avocats).

Usage : python3 graphismes_offre.py <feuille.png> <OpenSans_700Bold.ttf> <dossier_sortie>

Produit à 300 dpi : bandeau d'ouverture sombre, bandeau des pages suivantes, bandeau
de clôture (pied de page du verso) et logo en réserve (texte blanc) pour fond sombre.
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FEUILLE, POLICE_GRAS, SORTIE = sys.argv[1:4]
os.makedirs(SORTIE, exist_ok=True)

DPI = 300
mm = lambda v: round(v / 25.4 * DPI)

ARDOISE = (48, 72, 89)
ARDOISE_FONCE = (38, 58, 72)
VERT = (142, 195, 63)
BLANC = (255, 255, 255)


def feuille(largeur):
    im = Image.open(FEUILLE).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((largeur, round(im.height * largeur / im.width)), Image.LANCZOS)


def sur_echantillonner(dessin, taille, facteur=2):
    grand = Image.new("RGBA", (taille[0] * facteur, taille[1] * facteur), (0, 0, 0, 0))
    dessin(ImageDraw.Draw(grand), facteur)
    return grand.resize(taille, Image.LANCZOS)


def vague(pts_haut, W, H, k, bas, amplitude, phase, frequence=1.15):
    """Ajoute au polygone le bord ondulé, de droite à gauche."""
    for i in range(0, 201):
        x = W * (1 - i / 200)
        y = H * bas + H * amplitude * math.sin(i / 200 * math.pi * frequence + phase)
        pts_haut.append((x * k, y * k))
    return pts_haut


def logo_reserve():
    """Logo en réserve : même construction que le logo couleur, texte blanc."""
    police = ImageFont.truetype(POLICE_GRAS, 300)
    police_av = ImageFont.truetype(POLICE_GRAS, 205)
    cap = police.getbbox("V")[3] - police.getbbox("V")[1]
    w2 = police.getlength("& Préjudices")
    marge_g = round(w2 * 0.09)
    x_droite = marge_g + w2
    base1 = round(cap * 1.9)
    base2 = base1 + round(cap * 1.47)
    base3 = base2 + round(cap * 1.18)
    im = Image.new("RGBA", (round(x_droite) + 20, base3 + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((x_droite, base1), "Victimes", font=police, fill=BLANC, anchor="rs")
    d.text((marge_g, base2), "& Préjudices", font=police, fill=BLANC, anchor="ls")
    d.text((x_droite, base3), "Avocats", font=police_av, fill=VERT, anchor="rs")
    f = feuille(round(w2 * 0.32))
    im.alpha_composite(f, (max(0, marge_g - round(w2 * 0.069)), base1 + round(cap * 0.06) - f.height))
    im.crop(im.getbbox()).save(os.path.join(SORTIE, "logo_reserve.png"), dpi=(DPI, DPI))


def bandeau_ouverture(h_mm=103):
    W, H = mm(210), mm(h_mm)

    def dessin(d, k):
        d.polygon(vague([(0, 0), (W * k, 0)], W, H, k, 0.90, 0.05, -0.6), fill=ARDOISE)

    im = sur_echantillonner(dessin, (W, H))
    f = feuille(mm(74)).rotate(-4, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(f, (W - round(f.width * 0.70), mm(10)))
    im.save(os.path.join(SORTIE, "bandeau_ouverture.png"), dpi=(DPI, DPI))


def bandeau_suite(h_mm=15):
    W, H = mm(210), mm(h_mm)

    def dessin(d, k):
        d.polygon(vague([(0, 0), (W * k, 0)], W, H, k, 0.82, 0.10, 0.3, 1.1), fill=ARDOISE)

    im = sur_echantillonner(dessin, (W, H))
    f = feuille(mm(15))
    im.alpha_composite(f, (W - mm(16) - f.width, round((H * 0.78 - f.height) / 2)))
    im.save(os.path.join(SORTIE, "bandeau_suite.png"), dpi=(DPI, DPI))


def bandeau_cloture(h_mm=70):
    W, H = mm(210), mm(h_mm)

    def dessin(d, k):
        d.polygon(vague([(0, H * k), (W * k, H * k)], W, H, k, 0.08, 0.05, 2.2, 1.2), fill=ARDOISE)

    im = sur_echantillonner(dessin, (W, H))
    f = feuille(mm(21)).rotate(8, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(f, (W - mm(16) - f.width, mm(4)))
    im.save(os.path.join(SORTIE, "bandeau_cloture.png"), dpi=(DPI, DPI))


if __name__ == "__main__":
    logo_reserve()
    bandeau_ouverture()
    bandeau_suite()
    bandeau_cloture()
    print("ok")
