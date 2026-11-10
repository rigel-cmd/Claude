"""Bannière web 300 × 600 px de la campagne Gazette du Palais 2026, déclinée de la 4e de couverture :
recrutement d'un avocat associé salarié (H/F), en priorité, et podcast « Hervé Gerbi raconte ».

Usage : python3 generer_banniere.py <dossier_polices> [dossier_sortie]

- dossier_polices : dossier parcouru récursivement (un node_modules, par exemple) qui contient
  DMSerifDisplay_400Regular.ttf, DMSerifDisplay_400Regular_Italic.ttf, Poppins_600SemiBold.ttf,
  OpenSans_400Regular.ttf, OpenSans_600SemiBold.ttf et MaterialIcons-Regular.ttf ;
- dossier_sortie : par défaut, le dossier du script.

Produit :
- Banniere_300x600_animee.gif : l'offre (titre, argument, QR code de l'offre), un intermède podcast
  (QR code du podcast), puis de nouveau l'offre, sur laquelle la bannière s'arrête. Le cycle dure 9,9 s
  et se joue 3 fois (29,7 s) ;
- Banniere_300x600_fixe.jpg : la scène de l'offre, en image fixe (identique à la première et à la
  dernière image du GIF).

Mise en page : sous la photo, le pan coupé porte l'étiquette, le titre, le filet et l'argument. En pied,
sur crème, le QR code, sa légende et le logo. Pour le podcast, le pan passe en anthracite ; en pied, le QR
code du podcast et sa légende remplacent ceux de l'offre.

Pas de bouton : une bannière en image n'a qu'une adresse de clic, qui ne peut pas suivre l'alternance de
l'offre et du podcast. Les QR codes sont les seuls appels à l'action, chacun menant à sa page.

QR codes : modules de 4 px exactement, posés au pixel près (sans rééchantillonnage), foncés sur fond
clair, avec une zone claire de 12 px (3 modules) tout autour.

Le script échoue si un fichier dépasse 150 Ko, si le GIF relu ne redonne pas exactement les images
calculées, si la zone claire d'un QR code est encombrée ou si le pan s'approche à moins de 14 px du
visage. Les éléments communs aux deux formats sont dans banniere_commun.py.
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from banniere_commun import (ANTHRACITE, BLANC, CONTOUR_VISAGE, CREME, ENCRE, GRIS_CLAIR, ICONE_CASQUE,
                             ICONE_ESSOR, ICONE_GROUPE, ICONE_RETOUR, ICONES, OPEN_SANS, OPEN_SANS_DEMI,
                             ORANGE, ORANGE_TEXTE, POPPINS, RESSOURCES, ROUGE, SERIF, SERIF_ITALIQUE,
                             URL_OFFRE, URL_PODCAST, cadre, controler_visage, controler_zone_claire,
                             dessiner_qr, etiquette, livrer, lisere, logo, masque_lisse, matrice_qr, police,
                             texte_lisse, utiliser_polices)

ICI = os.path.dirname(os.path.abspath(__file__))

W, H = 300, 600
X0 = 22                      # marges latérales
X1 = W - X0
DECALAGE_PHOTO = 82          # rognage du haut de la photo : le haut des cheveux est coupé, le visage remonte
# Pan coupé : bord supérieur en diagonale, comme le pan crème de la 4e de couverture
PAN_GAUCHE, PAN_DROITE = 300, 256

# Grille verticale (lignes de base), commune à l'offre et au podcast
Y_ETIQUETTE = 324
Y_TITRE = (361, 395)
Y_FILET = 407
Y_ARGUMENT = 428
H_LISERE = 4

# Pied : QR code à gauche, sur la marge ; légende et logo à droite (logo calé sur la marge droite et sur
# le bas du QR code). Seuls appels à l'action, les QR codes sont grands : modules de 4 px
MODULE = 4                   # taille d'un module de QR code, en pixels
ZONE_CLAIRE = 12             # zone claire exigée autour des modules (3 modules)
COTE_QR = 33 * MODULE        # QR code de l'offre : version 4, 33 modules, soit 132 px
X_QR, Y_QR = X0, H - H_LISERE - ZONE_CLAIRE - COTE_QR
# Haut du pied crème, commun aux deux scènes : il commence avec la zone claire du QR code de l'offre, pour
# que le volet anthracite ne la réduise jamais ; il reste 8 px sous les jambages de l'argument
Y_PIED = Y_QR - ZONE_CLAIRE
assert Y_PIED - Y_ARGUMENT >= 12
X_COLONNE = X_QR + COTE_QR + 16
LARGEUR_LOGO = X1 - X_COLONNE

MARGE_VISAGE = 14            # distance minimale entre le bord du pan et le visage


# --------------------------------------------------------------------------
# Éléments fixes
# --------------------------------------------------------------------------
def masque_pan(decalage=0, bas=H):
    """Pan coupé. decalage > 0 abaisse le bord (volet montant) ; bas : le masque s'arrête au-dessus de
    cette ligne."""
    return masque_lisse([(0, PAN_GAUCHE + decalage), (W, PAN_DROITE + decalage), (W, bas), (0, bas)], W, H)


def photo():
    im = Image.open(os.path.join(RESSOURCES, "photo_herve_gerbi.jpg")).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=50, threshold=2))
    fond = Image.new("RGB", (W, H), ANTHRACITE)
    fond.paste(im, (0, -DECALAGE_PHOTO))
    return fond


def titre(d, lignes):
    for (texte, nom_police, taille, couleur), y in zip(lignes, Y_TITRE):
        d.text((X0 - 1, y), texte, font=police(nom_police, taille), fill=couleur, anchor="ls")


def position_qr(url):
    """Coin haut gauche des modules : le QR code du podcast (plus petit) est centré sur celui de l'offre."""
    cote = len(matrice_qr(url)) * MODULE
    return X_QR + (COTE_QR - cote) // 2, Y_QR + (COTE_QR - cote) // 2, cote


Y_LEGENDE = (Y_QR + 26, Y_QR + 45)    # lignes de base de « Scannez » et de la suite


def pied(im, url, suite, couleur_qr, couleur_verbe, decalage_fleche=0):
    """Pied crème : QR code, flèche et légende sur deux lignes, logo calé sur le bas du QR code.
    decalage_fleche < 0 : la flèche avance vers le QR code."""
    d = ImageDraw.Draw(im)
    d.rectangle((0, Y_PIED, W, H - H_LISERE - 1), fill=CREME)
    x, y, _ = position_qr(url)
    dessiner_qr(d, url, x, y, MODULE, couleur_qr)
    d.text((X_COLONNE + decalage_fleche, Y_LEGENDE[0] + 3), chr(ICONE_RETOUR), font=police(ICONES, 20),
           fill=couleur_verbe, anchor="ls")
    texte_lisse(im, X_COLONNE + 22, Y_LEGENDE[0], "Scannez", POPPINS, 16, couleur_verbe)
    texte_lisse(im, X_COLONNE + 22, Y_LEGENDE[1], suite, POPPINS, 12, ENCRE)
    lg = logo("logo.png", LARGEUR_LOGO)
    im.paste(lg, (X_COLONNE, Y_QR + COTE_QR - lg.height), lg)
    lisere(d, W, H, H_LISERE)


# --------------------------------------------------------------------------
# Scènes (contenu du pan et du pied, sur toute la hauteur ; la photo est ajoutée au montage)
# --------------------------------------------------------------------------
def scene_offre(decalage_fleche=0):
    im = Image.new("RGB", (W, H), CREME)
    d = ImageDraw.Draw(im)
    etiquette(im, X0, Y_ETIQUETTE, ICONE_GROUPE, "RECRUTEMENT · GRENOBLE", ROUGE)
    titre(d, [("Avocat associé", SERIF, 32, ENCRE), ("salarié (H/F)", SERIF, 32, ENCRE)])
    d.rectangle((X0, Y_FILET, X1 - 1, Y_FILET + 2), fill=ROUGE)
    # L'argument, tiré de l'offre : « Ce poste est créé dans une perspective rapide d'association »
    d.text((X0 - 2, Y_ARGUMENT + 4), chr(ICONE_ESSOR), font=police(ICONES, 20), fill=ROUGE, anchor="ls")
    d.text((X0 + 23, Y_ARGUMENT), "Perspective rapide d’association", font=police(OPEN_SANS_DEMI, 13),
           fill=ENCRE, anchor="ls")
    pied(im, URL_OFFRE, "pour postuler", ROUGE, ROUGE, decalage_fleche)
    return im


def scene_podcast():
    im = Image.new("RGB", (W, H), ANTHRACITE)
    d = ImageDraw.Draw(im)
    etiquette(im, X0, Y_ETIQUETTE, ICONE_CASQUE, "PODCAST", ORANGE)
    titre(d, [("Hervé Gerbi", SERIF, 32, BLANC), ("raconte", SERIF_ITALIQUE, 34, ORANGE)])
    d.rectangle((X0, Y_FILET, X1 - 1, Y_FILET + 2), fill=ORANGE)
    d.text((X0, Y_ARGUMENT), "Histoires vraies d’un avocat de victimes", font=police(OPEN_SANS, 13),
           fill=GRIS_CLAIR, anchor="ls")
    pied(im, URL_PODCAST, "pour écouter", ENCRE, ORANGE_TEXTE)
    return im


# --------------------------------------------------------------------------
# Montage
# --------------------------------------------------------------------------
def monter(scene, volet=None, decalage=0):
    """Photo + pan. volet : scène dont le pan monte par-dessus, son bord abaissé de `decalage` pixels.
    Le volet monte depuis le bas : le pied (QR code et légende) passe à sa scène dès la première image,
    pour que le QR code et sa légende correspondent toujours au titre qui l'emporte à l'écran."""
    im = PHOTO.copy()
    im.paste(scene, (0, 0), PAN)
    if volet is not None:
        im.paste(volet, (0, 0), masque_pan(decalage, bas=Y_PIED))
        im.paste(volet.crop((0, Y_PIED, W, H)), (0, Y_PIED))
    return cadre(im)


def volet(dessous, dessus, url_dessus, n=6, duree=50):
    """Images du volet : le pan de `dessus` monte par-dessus celui de `dessous`, en ralentissant.
    50 ms par image : 20 images par seconde, sous le plafond de 24 des régies qui suivent l'IAB."""
    course = Y_PIED - PAN_DROITE
    return [(monter(dessous, dessus, round(course * (1 - k / (n + 1)) ** 2)), duree, url_dessus)
            for k in range(1, n + 1)]


def coup_de_pouce():
    """La flèche de la légende avance de 2, 4 puis 2 px vers le QR code de l'offre."""
    return [(monter(scene_offre(dx)), 70, URL_OFFRE) for dx in (-2, -4, -2)]


CYCLE = 9900                 # 3 lectures : 29,7 s, sous la limite usuelle de 30 s


def images_animation():
    """Liste de (image RGB, durée en ms, adresse du QR code affiché en pied) pour un cycle. La première
    et la dernière image sont identiques : l'offre et son QR code."""
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
    PHOTO, PAN = photo(), masque_pan()
    contour = [(x, y - DECALAGE_PHOTO) for x, y in CONTOUR_VISAGE]
    ok = livrer(images_animation(), PHOTO, np.array(PAN) == 0,
                os.path.join(sortie, "Banniere_300x600_animee.gif"),
                os.path.join(sortie, "Banniere_300x600_fixe.jpg"),
                [lambda: controler_visage(PAN, contour, MARGE_VISAGE)], controle_image)
    sys.exit(0 if ok else 1)
