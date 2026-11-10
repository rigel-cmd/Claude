"""Bannière web 600 × 200 px de la campagne Gazette du Palais 2026 : déclinaison horizontale de la
bannière 300 × 600 (recrutement d'un avocat associé salarié (H/F), en priorité, et podcast « Hervé Gerbi
raconte »), avec le même contenu, la même animation et les mêmes QR codes.

Usage : python3 generer_banniere_600x200.py <dossier_polices> [dossier_sortie]

(mêmes polices que generer_banniere.py)

Produit :
- Banniere_600x200_animee.gif : l'offre, un intermède podcast, puis de nouveau l'offre, sur laquelle la
  bannière s'arrête. Le cycle dure 9,9 s et se joue 3 fois (29,7 s) ;
- Banniere_600x200_fixe.jpg : la scène de l'offre, en image fixe.

Mise en page, de gauche à droite :
- la photo, coupée en diagonale par le pan, comme sur la 4e de couverture ;
- sur le pan, l'étiquette, le titre, le filet et l'argument (crème pour l'offre, anthracite pour le
  podcast) ;
- à droite, sur crème dans les deux scènes, le QR code, sa légende et le logo.

Pas de bouton, comme pour la bannière 300 × 600 : les QR codes sont les seuls appels à l'action. Modules de
3 px (QR code de 99 px pour l'offre) : à 4 px, le QR code ne laisserait pas de place au texte.

Le script échoue si un fichier dépasse 150 Ko, si le GIF relu ne redonne pas exactement les images
calculées, si la zone claire d'un QR code est encombrée, si le pan s'approche à moins de 12 px du visage
ou si le haut de la tête est à moins de 10 px du bord.
"""

import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw

from banniere_commun import (ANTHRACITE, BLANC, CREME, ENCRE, GRIS_CLAIR, ICONE_ESSOR, ICONE_RETOUR, ICONES,
                             OPEN_SANS, OPEN_SANS_DEMI, ORANGE, ORANGE_TEXTE, POPPINS, ROUGE, SERIF,
                             SERIF_ITALIQUE, URL_OFFRE, URL_PODCAST, cadre, contour_visage, controler_cadrage,
                             controler_visage, controler_zone_claire, dessiner_qr, livrer, lisere, logo,
                             masque_lisse, matrice_qr, photo, police, texte_lisse, utiliser_polices)

ICI = os.path.dirname(os.path.abspath(__file__))

W, H = 600, 200
H_LISERE = 4
H_UTILE = H - H_LISERE

# Photo : la ressource (629 px de large) est réduite à ECHELLE, puis décalée de (DX, DY) ; la tête entière
# tient dans la hauteur, avec de l'air au-dessus des cheveux
ECHELLE, DX, DY = 0.2715, 9, 12
MARGE_TETE = 10
# Pan coupé : bord gauche en diagonale, plus à droite en haut qu'en bas, comme le pan de la 4e de couverture
PAN_HAUT, PAN_BAS = 160, 128
MARGE_VISAGE = 12

# Colonne du texte, sur le pan. L'étiquette n'a pas de pictogramme dans ce format : « RECRUTEMENT ·
# GRENOBLE » n'aurait pas tenu avant la colonne du QR code
X0 = 172
APPROCHE_ETIQUETTE = 1.2
Y_ETIQUETTE = 44
Y_TITRE = (76, 104)
Y_FILET = 114
Y_CORPS = (134, 150)

# Colonne de droite, crème dans les deux scènes : QR code, puis légende et logo à sa droite
MODULE = 3
ZONE_CLAIRE = 12             # zone claire exigée autour des modules (4 modules)
COTE_QR = 33 * MODULE        # QR code de l'offre : version 4, 33 modules, soit 99 px
X_QR, Y_QR = 372, (H_UTILE - COTE_QR) // 2
X_PIED = X_QR - ZONE_CLAIRE  # début du fond crème commun aux deux scènes
X_COLONNE = X_QR + COTE_QR + 14
X1 = W - 22
LARGEUR_LOGO = X1 - X_COLONNE
Y_LEGENDE = (Y_QR + 22, Y_QR + 40)    # lignes de base de « Scannez » et de la suite


# --------------------------------------------------------------------------
# Éléments fixes
# --------------------------------------------------------------------------
def masque_pan():
    return masque_lisse([(PAN_HAUT, 0), (W, 0), (W, H), (PAN_BAS, H)], W, H)


def position_qr(url):
    """Coin haut gauche des modules : le QR code du podcast (plus petit) est centré sur celui de l'offre."""
    cote = len(matrice_qr(url)) * MODULE
    return X_QR + (COTE_QR - cote) // 2, Y_QR + (COTE_QR - cote) // 2, cote


def colonne_qr(im, url, suite, couleur_qr, couleur_verbe, decalage_fleche=0):
    """Fond crème à droite : QR code, flèche et légende sur deux lignes, logo calé sur le bas du QR code.
    decalage_fleche < 0 : la flèche avance vers le QR code."""
    d = ImageDraw.Draw(im)
    d.rectangle((X_PIED, 0, W, H), fill=CREME)
    x, y, _ = position_qr(url)
    dessiner_qr(d, url, x, y, MODULE, couleur_qr)
    d.text((X_COLONNE + decalage_fleche, Y_LEGENDE[0] + 3), chr(ICONE_RETOUR), font=police(ICONES, 20),
           fill=couleur_verbe, anchor="ls")
    texte_lisse(im, X_COLONNE + 22, Y_LEGENDE[0], "Scannez", POPPINS, 16, couleur_verbe)
    texte_lisse(im, X_COLONNE + 22, Y_LEGENDE[1], suite, POPPINS, 12, ENCRE)
    lg = logo("logo.png", LARGEUR_LOGO)
    im.paste(lg, (X_COLONNE, Y_QR + COTE_QR - lg.height), lg)


def etiquette(im, texte, couleur):
    """Capitales espacées, comme sur la 4e de couverture ; elles s'arrêtent avant la colonne du QR code."""
    texte_lisse(im, X0, Y_ETIQUETTE, texte, POPPINS, 11, couleur, approche=APPROCHE_ETIQUETTE)
    fin = X0 + sum(police(POPPINS, 11).getlength(c) + APPROCHE_ETIQUETTE for c in texte)
    assert fin <= X_PIED - 14, f"étiquette trop longue : elle finit à {fin:.0f} px"


def titre(d, lignes):
    for (texte, nom_police, taille, couleur), y in zip(lignes, Y_TITRE):
        d.text((X0 - 1, y), texte, font=police(nom_police, taille), fill=couleur, anchor="ls")


def filet(d, couleur):
    d.rectangle((X0, Y_FILET, X_PIED - 14, Y_FILET + 2), fill=couleur)


# --------------------------------------------------------------------------
# Scènes (contenu du pan et de la colonne de droite ; la photo est ajoutée au montage)
# --------------------------------------------------------------------------
def scene_offre(decalage_fleche=0):
    im = Image.new("RGB", (W, H), CREME)
    d = ImageDraw.Draw(im)
    etiquette(im, "RECRUTEMENT · GRENOBLE", ROUGE)
    titre(d, [("Avocat associé", SERIF, 26, ENCRE), ("salarié (H/F)", SERIF, 26, ENCRE)])
    filet(d, ROUGE)
    # L'argument, tiré de l'offre : « Ce poste est créé dans une perspective rapide d'association »
    d.text((X0 - 2, Y_CORPS[0] + 4), chr(ICONE_ESSOR), font=police(ICONES, 20), fill=ROUGE, anchor="ls")
    for texte, y in zip(("Perspective rapide", "d’association"), Y_CORPS):
        d.text((X0 + 23, y), texte, font=police(OPEN_SANS_DEMI, 12), fill=ENCRE, anchor="ls")
    colonne_qr(im, URL_OFFRE, "pour postuler", ROUGE, ROUGE, decalage_fleche)
    return im


def scene_podcast():
    im = Image.new("RGB", (W, H), ANTHRACITE)
    d = ImageDraw.Draw(im)
    etiquette(im, "PODCAST", ORANGE)
    titre(d, [("Hervé Gerbi", SERIF, 26, BLANC), ("raconte", SERIF_ITALIQUE, 28, ORANGE)])
    filet(d, ORANGE)
    for texte, y in zip(("Histoires vraies d’un avocat", "de victimes"), Y_CORPS):
        d.text((X0, y), texte, font=police(OPEN_SANS, 12), fill=GRIS_CLAIR, anchor="ls")
    colonne_qr(im, URL_PODCAST, "pour écouter", ENCRE, ORANGE_TEXTE)
    return im


# --------------------------------------------------------------------------
# Montage
# --------------------------------------------------------------------------
PENTE = 30                   # inclinaison du bord du volet, qui monte vers la droite


def masque_volet(d):
    """Partie du pan, hors colonne de droite, sous un bord incliné placé à d px du haut (côté droit)."""
    m = masque_lisse([(0, d + PENTE), (X_PIED, d), (X_PIED, H), (0, H)], W, H)
    return ImageChops.multiply(m, PAN)


def monter(scene, volet=None, d=0):
    """Photo + pan + liseré. volet : scène dont le pan monte par-dessus (bord à d px du haut). La colonne
    de droite passe à cette scène dès la première image du volet, pour que le QR code et sa légende
    correspondent toujours au titre qui l'emporte à l'écran."""
    im = PHOTO.copy()
    im.paste(scene, (0, 0), PAN)
    if volet is not None:
        im.paste(volet, (0, 0), masque_volet(d))
        im.paste(volet.crop((X_PIED, 0, W, H)), (X_PIED, 0))
    lisere(ImageDraw.Draw(im), W, H, H_LISERE)
    return cadre(im)


def volet(dessous, dessus, url_dessus, n=6, duree=50):
    """Images du volet : le pan de `dessus` monte par-dessus celui de `dessous`, en ralentissant."""
    course = H + PENTE
    return [(monter(dessous, dessus, round(-PENTE + course * (1 - k / (n + 1)) ** 2)), duree, url_dessus)
            for k in range(1, n + 1)]


def coup_de_pouce():
    """La flèche de la légende avance de 2, 4 puis 2 px vers le QR code de l'offre."""
    return [(monter(scene_offre(dx)), 70, URL_OFFRE) for dx in (-2, -4, -2)]


CYCLE = 9900                 # 3 lectures : 29,7 s, sous la limite usuelle de 30 s


def images_animation():
    """Même déroulé que la bannière 300 × 600. La première et la dernière image sont identiques."""
    offre, podcast = scene_offre(), scene_podcast()
    images = [(monter(offre), 1500, URL_OFFRE)] + coup_de_pouce() + [(monter(offre), 1100, URL_OFFRE)]
    images += volet(offre, podcast, URL_PODCAST)            # volet anthracite : le podcast
    images.append((monter(podcast), 2900, URL_PODCAST))
    images += volet(podcast, offre, URL_OFFRE)              # volet crème : retour à l'offre
    images += [(monter(offre), 1000, URL_OFFRE)] + coup_de_pouce()
    images.append((monter(offre), CYCLE - sum(d for _, d, _ in images), URL_OFFRE))
    return images


def controle_image(im, url, nom):
    x, y, cote = position_qr(url)
    return controler_zone_claire(im, x, y, cote, ZONE_CLAIRE, nom)


if __name__ == "__main__":
    utiliser_polices(sys.argv[1])
    sortie = sys.argv[2] if len(sys.argv) > 2 else ICI
    os.makedirs(sortie, exist_ok=True)
    PHOTO, PAN = photo(W, H, ECHELLE, DX, DY), masque_pan()
    assert PHOTO.getpixel((PAN_HAUT + 1, 0)) != ANTHRACITE, "la photo ne couvre pas tout le coin haut"
    visible = np.array(PAN) == 0
    visible[H - H_LISERE:, :] = False                      # le liseré passe sous la photo
    ok = livrer(images_animation(), PHOTO, visible,
                os.path.join(sortie, "Banniere_600x200_animee.gif"),
                os.path.join(sortie, "Banniere_600x200_fixe.jpg"),
                [lambda: controler_visage(PAN, contour_visage(ECHELLE, DX, DY), MARGE_VISAGE),
                 lambda: controler_cadrage(ECHELLE, DY, MARGE_TETE)], controle_image)
    sys.exit(0 if ok else 1)
