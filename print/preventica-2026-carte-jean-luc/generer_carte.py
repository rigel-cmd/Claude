"""Carte carrée recto verso — épisode « Jean-Luc » du podcast Hervé Gerbi Raconte.

Génère un PDF prêt pour l'impression : format fini 65 x 65 mm, fond perdu 3 mm
(page 71 x 71 mm, TrimBox/BleedBox renseignés), couleurs vectorielles en CMJN
d'après la palette élargie Victimes & Préjudices.

    pip install reportlab qrcode pillow pymupdf
    python generer_carte.py
"""
from pathlib import Path

import qrcode
from PIL import Image
from reportlab.lib.colors import CMYKColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ICI = Path(__file__).parent
ASSETS = ICI / "assets"

EPISODE_URL = (
    "https://smartlink.ausha.co/herve-gerbi-raconte-histoire-vraies-d-un-avocat-des-victimes/"
    "jean-luc-ecrase-par-une-machine-sur-son-lieu-de-travail"
)

FINI = 65 * mm   # format fini
FP = 3 * mm      # fond perdu
PAGE = FINI + 2 * FP
MARGE = 5 * mm   # zone de sécurité


def cmjn(c, m, j, n):
    return CMYKColor(c / 100, m / 100, j / 100, n / 100)


# Palette élargie (valeurs CMJN de la charte)
CREME = cmjn(2, 3, 25, 0)        # 7499 C  #FAF0C7
ROUGE = cmjn(20, 100, 98, 11)    # 1805 C  #B52026
JAUNE = cmjn(0, 35, 99, 0)       # 130 C   #FCAF19
VERT = cmjn(50, 2, 100, 0)       # 7488 C  #8EC33F
GRIS_FONCE = cmjn(69, 63, 62, 58)  # Black C #333333
BLANC = cmjn(0, 0, 0, 0)
NOIR_RICHE = cmjn(60, 40, 40, 100)

for nom, fichier in {
    "Poppins-SemiBold": "Poppins-600.ttf",
    "Poppins-Bold": "Poppins-700.ttf",
    "OpenSans": "OpenSans-400.ttf",
    "OpenSans-SemiBold": "OpenSans-600.ttf",
}.items():
    pdfmetrics.registerFont(TTFont(nom, str(ASSETS / "fonts" / fichier)))


def xy(x, y_haut):
    """Coordonnées en mm depuis le coin haut-gauche du format fini."""
    return FP + x * mm, PAGE - FP - y_haut * mm


def texte(c, x, y, s, police, corps, couleur, espacement=0, aligne="g"):
    c.setFillColor(couleur)
    px, py = xy(x, y)
    largeur = pdfmetrics.stringWidth(s, police, corps) + espacement * max(len(s) - 1, 0)
    if aligne == "d":
        px -= largeur
    t = c.beginText(px, py)
    t.setFont(police, corps)
    t.setCharSpace(espacement)
    t.textOut(s)
    c.drawText(t)


def paves(c, x, y, lignes, police, corps, interligne, couleur):
    for i, ligne in enumerate(lignes):
        texte(c, x, y + i * interligne, ligne, police, corps, couleur)


def fond(c, couleur):
    c.setFillColor(couleur)
    c.rect(0, 0, PAGE, PAGE, stroke=0, fill=1)


def recto(c):
    # La couverture a un fond noir : on l'étend au fond perdu et on la réduit
    # légèrement pour que les titres restent dans la zone de sécurité.
    fond(c, NOIR_RICHE)
    couv = Image.open(ASSETS / "couverture-jean-luc.jpg").convert("RGB")
    w, h = couv.size
    couv = couv.crop((6, 6, w - 6, h - 6))  # retire le liseré clair du bord
    cote = 60 * mm
    decal = (PAGE - cote) / 2
    c.drawImage(ImageReader(couv), decal, decal, cote, cote)

    # Sous-titre de l'épisode, aligné à droite sur « JEAN-LUC »
    droite = 2.5 + 60 * 1836 / 2000
    texte(c, droite, 48.7, "Écrasé par une machine sur son lieu de travail",
          "OpenSans", 6.5, BLANC, aligne="d")


def dessiner_qr(c, x, y, cote):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    qr.add_data(EPISODE_URL)
    qr.make(fit=True)
    matrice = qr.get_matrix()
    n = len(matrice)
    module = cote * mm / n
    x0, y0 = xy(x, y)
    c.setFillColor(GRIS_FONCE)
    for i, rang in enumerate(matrice):
        j = 0
        while j < n:  # fusionne les modules contigus pour un tracé propre
            if rang[j]:
                k = j
                while k < n and rang[k]:
                    k += 1
                c.rect(x0 + j * module, y0 - (i + 1) * module,
                       (k - j) * module, module, stroke=0, fill=1)
                j = k
            else:
                j += 1
    return qr.version, n, cote / n


def verso(c):
    fond(c, CREME)

    # En-tête podcast
    texte(c, MARGE / mm, 9, "LE PODCAST", "Poppins-SemiBold", 6, ROUGE, espacement=1.1)
    texte(c, MARGE / mm, 15.2, "Hervé Gerbi raconte", "Poppins-Bold", 12.5, GRIS_FONCE)
    texte(c, MARGE / mm, 19.6, "Histoires vraies d'un avocat des victimes",
          "OpenSans", 6.6, GRIS_FONCE)
    c.setFillColor(JAUNE)
    c.rect(*xy(5, 22.6), 9 * mm, 0.9 * mm, stroke=0, fill=1)

    # Épisode (colonne gauche)
    texte(c, 5, 29, "ÉPISODE", "Poppins-SemiBold", 5.6, ROUGE, espacement=1)
    texte(c, 5, 34.4, "Jean-Luc", "Poppins-Bold", 11, GRIS_FONCE)
    paves(c, 5, 39, ["Écrasé par une machine", "sur son lieu de travail."],
          "OpenSans", 6.6, 3.1, GRIS_FONCE)
    texte(c, 5, 47.2, "Scannez pour écouter", "OpenSans-SemiBold", 6.2, ROUGE)

    # QR code sur pastille blanche (zone de silence ≥ 2 modules)
    c.setFillColor(BLANC)
    c.roundRect(*xy(35.5, 49.5), 24.5 * mm, 24.5 * mm, 1.6 * mm, stroke=0, fill=1)
    version, n, module_mm = dessiner_qr(c, 37.25, 26.75, 21)

    # Bandeau cabinet (déborde dans le fond perdu)
    haut = 52.5
    c.setFillColor(GRIS_FONCE)
    c.rect(0, 0, PAGE, FP + (65 - haut) * mm, stroke=0, fill=1)
    c.setFillColor(ROUGE)
    c.rect(0, FP + (65 - haut) * mm, PAGE, 0.6 * mm, stroke=0, fill=1)

    feuilles = Image.open(ASSETS / "logo-feuilles.png")
    lw = 6.5 * mm
    lh = lw * feuilles.height / feuilles.width
    fx, fy = xy(5, 58.8)
    c.drawImage(ImageReader(feuilles), fx, fy - lh / 2, lw, lh, mask="auto")
    texte(c, 12.8, 58, "Victimes & Préjudices", "Poppins-SemiBold", 6.2, BLANC)
    texte(c, 12.8, 61, "Avocats", "Poppins-SemiBold", 5.2, VERT)
    texte(c, 60, 58, "victimesetprejudices.fr", "OpenSans", 5, BLANC, aligne="d")
    texte(c, 60, 61, "04 76 87 29 19", "OpenSans", 5, BLANC, aligne="d")
    return version, n, module_mm


def boites(c):
    c.setPageSize((PAGE, PAGE))
    c.setTrimBox((FP, FP, FP + FINI, FP + FINI))
    c.setBleedBox((0, 0, PAGE, PAGE))


def main():
    sortie = ICI / "carte-jean-luc-65x65-fond-perdu-3mm.pdf"
    c = canvas.Canvas(str(sortie), pagesize=(PAGE, PAGE))
    c.setTitle("Carte Hervé Gerbi Raconte – Jean-Luc (65x65 mm)")
    c.setAuthor("Victimes & Préjudices Avocats")
    boites(c)
    recto(c)
    c.showPage()
    boites(c)
    version, n, module_mm = verso(c)
    c.showPage()
    c.save()
    print(f"{sortie.name} — QR v{version}, {n} modules, {module_mm:.2f} mm/module")

    # Aperçus PNG (format fini, sans fond perdu)
    try:
        import pymupdf as fitz
    except ImportError:
        return
    doc = fitz.open(sortie)
    for page, nom in zip(doc, ("recto", "verso")):
        pix = page.get_pixmap(dpi=300, clip=fitz.Rect(FP, FP, FP + FINI, FP + FINI))
        pix.save(ICI / f"apercu-{nom}.png")


if __name__ == "__main__":
    main()
