"""Génère les éléments graphiques de la fiche (charte Victimes & Préjudices Avocats).

Usage : python3 graphismes.py <feuille.png> <dossier_polices> <MaterialIcons-Regular.ttf> <dossier_sortie>

- feuille.png : symbole du logo (deux feuilles, fond transparent) ;
- dossier_polices : contient OpenSans_700Bold.ttf ;
- MaterialIcons-Regular.ttf : police d'icônes Material Icons (Apache 2.0).

Tous les visuels sont produits à 300 dpi.
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FEUILLE, POLICES, ICONES, SORTIE = sys.argv[1:5]
os.makedirs(SORTIE, exist_ok=True)

DPI = 300
mm = lambda v: round(v / 25.4 * DPI)

CREME = (250, 240, 199)
ROUGE = (181, 32, 38)
ORANGE = (252, 175, 25)
VERT = (142, 195, 63)
BLEU_CLAIR = (188, 222, 240)
ARDOISE = (48, 72, 89)
ANTHRACITE = (51, 51, 51)
BLANC = (255, 255, 255)


def feuille(largeur):
    im = Image.open(FEUILLE).convert("RGBA")
    im = im.crop(im.getbbox())
    h = round(im.height * largeur / im.width)
    return im.resize((largeur, h), Image.LANCZOS)


def sur_echantillonner(dessin, taille, facteur=4):
    """Dessine à 4x puis réduit, pour des contours lissés."""
    grand = Image.new("RGBA", (taille[0] * facteur, taille[1] * facteur), (0, 0, 0, 0))
    dessin(ImageDraw.Draw(grand), facteur)
    return grand.resize(taille, Image.LANCZOS)


# --------------------------------------------------------------------------
# Logo (symbole + nom du cabinet), reconstitué en haute définition
# --------------------------------------------------------------------------
def logo():
    """Proportions relevées sur le logo officiel : symbole à gauche au-dessus de « & »,
    nom en Open Sans Bold anthracite, « Avocats » en vert, bloc aligné à droite."""
    gras = os.path.join(POLICES, "OpenSans_700Bold.ttf")
    police = ImageFont.truetype(gras, 300)
    police_av = ImageFont.truetype(gras, 205)
    l1, l2, l3 = "Victimes", "& Préjudices", "Avocats"
    cap = police.getbbox("V")[3] - police.getbbox("V")[1]
    w2 = police.getlength(l2)
    marge_g = round(w2 * 0.09)
    x_droite = marge_g + w2
    base1 = round(cap * 1.9)
    base2 = base1 + round(cap * 1.47)
    base3 = base2 + round(cap * 1.18)
    im = Image.new("RGBA", (round(x_droite) + 20, base3 + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((x_droite, base1), l1, font=police, fill=ANTHRACITE, anchor="rs")
    d.text((marge_g, base2), l2, font=police, fill=ANTHRACITE, anchor="ls")
    d.text((x_droite, base3), l3, font=police_av, fill=VERT, anchor="rs")
    f = feuille(round(w2 * 0.32))
    im.alpha_composite(f, (max(0, marge_g - round(w2 * 0.069)), base1 + round(cap * 0.06) - f.height))
    im = im.crop(im.getbbox())
    im.save(os.path.join(SORTIE, "logo.png"), dpi=(DPI, DPI))
    return im.size


# --------------------------------------------------------------------------
# Bandeau de la première page (fond crème, vague, grande feuille à droite)
# --------------------------------------------------------------------------
def bandeau_p1(h_mm=82):
    W, H = mm(210), mm(h_mm)

    def dessin(d, k):
        pts = [(0, 0), (W * k, 0)]
        for i in range(0, 201):
            x = W * (1 - i / 200)
            y = H * 0.86 + H * 0.07 * math.sin(i / 200 * math.pi * 1.15 + 0.4)
            pts.append((x * k, y * k))
        d.polygon(pts, fill=CREME)

    im = sur_echantillonner(dessin, (W, H), 2)
    f = feuille(mm(78)).rotate(-4, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(f, (W - round(f.width * 0.74), mm(9)))
    im.save(os.path.join(SORTIE, "bandeau_p1.png"), dpi=(DPI, DPI))


# --------------------------------------------------------------------------
# Bandeau des pages suivantes
# --------------------------------------------------------------------------
def bandeau_p2(h_mm=17):
    W, H = mm(210), mm(h_mm)

    def dessin(d, k):
        pts = [(0, 0), (W * k, 0)]
        for i in range(0, 201):
            x = W * (1 - i / 200)
            y = H * 0.80 + H * 0.12 * math.sin(i / 200 * math.pi * 1.1 + 0.3)
            pts.append((x * k, y * k))
        d.polygon(pts, fill=CREME)

    im = sur_echantillonner(dessin, (W, H), 2)
    f = feuille(mm(17))
    im.alpha_composite(f, (W - mm(16) - f.width, round((H * 0.8 - f.height) / 2)))
    im.save(os.path.join(SORTIE, "bandeau_p2.png"), dpi=(DPI, DPI))


# --------------------------------------------------------------------------
# Liseré tricolore de pied de page
# --------------------------------------------------------------------------
def lisere():
    W, H = mm(210), mm(2.2)
    im = Image.new("RGB", (W, H), ROUGE)
    d = ImageDraw.Draw(im)
    d.rectangle((round(W * 0.55), 0, round(W * 0.82), H), fill=ORANGE)
    d.rectangle((round(W * 0.82), 0, W, H), fill=VERT)
    im.save(os.path.join(SORTIE, "lisere.png"), dpi=(DPI, DPI))


# --------------------------------------------------------------------------
# Frise chronologique : filet et quatre jalons aux centres de quatre colonnes égales
# --------------------------------------------------------------------------
def frise(largeur_mm=178, n=4):
    W, H = mm(largeur_mm), mm(7)
    couleurs = [ROUGE, ORANGE, VERT, ARDOISE]

    def dessin(d, k):
        y = H * k / 2
        d.rounded_rectangle((W * k / (2 * n), y - mm(0.45) * k, W * k * (1 - 1 / (2 * n)), y + mm(0.45) * k),
                            radius=mm(0.45) * k, fill=(214, 211, 211))
        for i in range(n):
            cx = W * k * (2 * i + 1) / (2 * n)
            r = mm(3.1) * k
            d.ellipse((cx - r, y - r, cx + r, y + r), fill=BLANC)
            r2 = mm(2.3) * k
            d.ellipse((cx - r2, y - r2, cx + r2, y + r2), fill=couleurs[i])

    sur_echantillonner(dessin, (W, H)).save(os.path.join(SORTIE, "frise.png"), dpi=(DPI, DPI))


# --------------------------------------------------------------------------
# Pastilles et pictogrammes (Material Icons)
# --------------------------------------------------------------------------
def icone(nom, code, couleur, taille_mm, fond=None, echelle=0.58):
    T = mm(taille_mm)

    def dessin(d, k):
        if fond:
            d.ellipse((0, 0, T * k - 1, T * k - 1), fill=fond)
        police = ImageFont.truetype(ICONES, round(T * k * (echelle if fond else 0.98)))
        d.text((T * k / 2, T * k / 2), chr(code), font=police, fill=couleur, anchor="mm")

    sur_echantillonner(dessin, (T, T)).save(os.path.join(SORTIE, f"{nom}.png"), dpi=(DPI, DPI))


if __name__ == "__main__":
    print("logo", logo())
    bandeau_p1()
    bandeau_p2()
    lisere()
    frise()
    # Pastilles de section : cercle plein couleur de section, pictogramme blanc
    icone("pastille_cep", 0xE87A, BLANC, 12, fond=ROUGE)          # explore
    icone("pastille_vae", 0xE7AF, BLANC, 12, fond=ORANGE)         # workspace_premium
    icone("pastille_cpf", 0xE80C, BLANC, 12, fond=VERT)           # school
    icone("pastille_dot", 0xEBCB, BLANC, 12, fond=ARDOISE)        # handshake
    # Pictogrammes de contact et d'action
    icone("ico_tel", 0xE0B0, ROUGE, 4)          # call
    icone("ico_web", 0xE894, ROUGE, 4)          # language
    icone("ico_horaires", 0xE8B5, ROUGE, 4)     # schedule
    icone("ico_lieu", 0xE55F, ROUGE, 4)         # place
    icone("ico_case", 0xE835, ROUGE, 4.6)       # check_box_outline_blank
    icone("ico_idee", 0xE0F0, ORANGE, 9, fond=(254, 243, 221), echelle=0.62)  # lightbulb
    icone("ico_notes", 0xE745, ARDOISE, 5)      # edit_note
    print("ok")
