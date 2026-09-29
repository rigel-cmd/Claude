"""Vectorise la feuille du logo (deux couleurs) en SVG, pour la version web de l'offre.

Usage : python3 vectoriser_feuille.py <feuille.png> <sortie.svg>
Prérequis : pip install potracer pillow numpy
"""

import sys

import numpy as np
import potrace
from PIL import Image, ImageFilter

SOURCE, SORTIE = sys.argv[1:3]
COULEURS = {"#F8A900": (248, 169, 0), "#B20426": (178, 4, 38)}  # orange derrière, rouge devant

im = Image.open(SOURCE).convert("RGBA")
im = im.crop(im.getbbox())
px = np.asarray(im).astype(int)
L, H = im.size


def pt(p):
    x, y = (p.x, p.y) if hasattr(p, "x") else p
    return f"{x:.1f} {y:.1f}"


def masque_couleur(rgb):
    return (np.abs(px[:, :, :3] - rgb).sum(axis=2) < 90) & (px[:, :, 3] > 128)


def dilater(m, n):
    return np.asarray(Image.fromarray(m.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(n))) > 0


rouge = masque_couleur(COULEURS["#B20426"])
chemins = []
for hexa, rgb in COULEURS.items():
    masque = masque_couleur(rgb)
    if hexa == "#F8A900":  # l'orange passe sous le rouge : pas de liseré clair à la jonction
        masque = masque | (dilater(masque, 9) & rouge)
    # potracer trace les pixels « faux » : on lui passe le complément du masque
    courbes = potrace.Bitmap(~masque).trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.2)
    d = []
    for courbe in courbes:
        d.append("M" + pt(courbe.start_point))
        for s in courbe.segments:
            if s.is_corner:
                d.append("L" + pt(s.c) + "L" + pt(s.end_point))
            else:
                d.append("C" + pt(s.c1) + " " + pt(s.c2) + " " + pt(s.end_point))
        d.append("Z")
    chemins.append(f'<path fill="{hexa}" d="{"".join(d)}"/>')

with open(SORTIE, "w", encoding="utf8") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {L} {H}">{"".join(chemins)}</svg>\n')
print(f"{SORTIE} : {L}×{H}")
