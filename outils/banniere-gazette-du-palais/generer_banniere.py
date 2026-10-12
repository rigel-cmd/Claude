"""Bannière web 300 × 600 px de la campagne Gazette du Palais 2026, déclinée de la 4e de couverture :
podcast « Hervé Gerbi raconte » et recrutement d'un avocat associé salarié (H/F).

Usage : python3 generer_banniere.py <dossier_polices> [dossier_sortie]

- dossier_polices : dossier parcouru récursivement (un node_modules, par exemple) qui contient
  DMSerifDisplay_400Regular.ttf, DMSerifDisplay_400Regular_Italic.ttf, Poppins_600SemiBold.ttf,
  OpenSans_400Regular.ttf et MaterialIcons-Regular.ttf ;
- dossier_sortie : par défaut, le dossier du script.

Produit :
- Banniere_300x600_animee.gif : trois scènes (podcast, recrutement, appel à l'action). Le cycle dure
  10 s et se joue 3 fois (30 s), puis la bannière s'arrête sur la scène finale ;
- Banniere_300x600_fixe.jpg : la scène finale, en image fixe.

La photo reste identique d'une image à l'autre (mêmes index de palette) : seul le pan coupé change,
ce qui garde le GIF léger. Le poids de chaque fichier est contrôlé (150 Ko maximum).
"""

import functools
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
POLICES = sys.argv[1]
SORTIE = sys.argv[2] if len(sys.argv) > 2 else ICI
RESSOURCES = os.path.join(ICI, "ressources")
POIDS_MAX = 150_000            # 150 Ko, au sens strict (150 000 octets)

W, H = 300, 600
X0 = 22                      # marge gauche du texte
LARGEUR_UTILE = W - 2 * X0
DECALAGE_PHOTO = 22          # rognage du haut de la photo (cheveux au ras du bord)
# Pan coupé : bord supérieur en diagonale, comme le pan crème de la 4e de couverture
PAN_GAUCHE, PAN_DROITE = 372, 306

# Grille verticale du pan (lignes de base)
Y_ETIQUETTE = 398
Y_TITRE = (438, 474)
Y_FILET = 488
Y_CORPS = (509, 527)
H_BOUTON = 34
Y_LOGO = 540
LARGEUR_LOGO = 104
H_LISERE = 4

# Couleurs relevées sur la 4e de couverture
CREME = (244, 240, 231)
ANTHRACITE = (51, 51, 51)
ROUGE = (181, 32, 38)
ORANGE = (252, 175, 25)
VERT = (142, 195, 63)
ENCRE = (21, 31, 36)
TEXTE = (59, 70, 73)
BLANC = (255, 255, 255)
GRIS_CLAIR = (232, 232, 232)
CADRE = (196, 190, 178)

ICONE_CASQUE, ICONE_GROUPE, ICONE_FLECHE = 0xF01F, 0xF233, 0xE5C8


@functools.lru_cache(maxsize=None)
def chemin_police(nom):
    for racine, _, fichiers in os.walk(POLICES):
        if nom in fichiers:
            return os.path.join(racine, nom)
    sys.exit(f"Police introuvable dans {POLICES} : {nom}")


@functools.lru_cache(maxsize=None)
def police(nom, taille):
    return ImageFont.truetype(chemin_police(nom), taille)


SERIF = "DMSerifDisplay_400Regular.ttf"
SERIF_ITALIQUE = "DMSerifDisplay_400Regular_Italic.ttf"
POPPINS = "Poppins_600SemiBold.ttf"
OPEN_SANS = "OpenSans_400Regular.ttf"
ICONES = "MaterialIcons-Regular.ttf"


# --------------------------------------------------------------------------
# Éléments fixes
# --------------------------------------------------------------------------
def masque_pan(decalage=0, k=4):
    """Pan coupé, lissé par suréchantillonnage. decalage > 0 abaisse le bord (volet montant)."""
    m = Image.new("L", (W * k, H * k), 0)
    ImageDraw.Draw(m).polygon(
        [(0, (PAN_GAUCHE + decalage) * k), (W * k, (PAN_DROITE + decalage) * k), (W * k, H * k), (0, H * k)],
        fill=255)
    return m.resize((W, H), Image.LANCZOS)


def photo():
    im = Image.open(os.path.join(RESSOURCES, "photo_herve_gerbi.jpg")).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=50, threshold=2))
    fond = Image.new("RGB", (W, H), ANTHRACITE)
    fond.paste(im, (0, -DECALAGE_PHOTO))
    return fond


@functools.lru_cache(maxsize=None)
def logo(fichier):
    im = Image.open(os.path.join(RESSOURCES, fichier)).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((LARGEUR_LOGO, round(im.height * LARGEUR_LOGO / im.width)), Image.LANCZOS)


def lisere(d):
    y = H - H_LISERE
    d.rectangle((0, y, round(W * 0.55) - 1, H), fill=ROUGE)
    d.rectangle((round(W * 0.55), y, round(W * 0.82) - 1, H), fill=ORANGE)
    d.rectangle((round(W * 0.82), y, W, H), fill=VERT)


def etiquette(im, code, texte, couleur, k=4):
    ImageDraw.Draw(im).text((X0 - 1, Y_ETIQUETTE + 1), chr(code), font=police(ICONES, 20), fill=couleur,
                            anchor="ls")
    # Capitales espacées, comme sur la 4e de couverture. Tracées 4 fois plus grandes puis réduites :
    # au pixel près, l'espacement des lettres serait irrégulier.
    f = police(POPPINS, 11 * k)
    masque = Image.new("L", (W * k, 30 * k), 0)
    d = ImageDraw.Draw(masque)
    x = (X0 + 26) * k
    for lettre in texte:
        d.text((x, 20 * k), lettre, font=f, fill=255, anchor="ls")
        x += f.getlength(lettre) + 1.7 * k
    masque = masque.resize((W, 30), Image.LANCZOS)
    im.paste(couleur, (0, Y_ETIQUETTE - 23), masque)


def titre(d, lignes):
    for (texte, nom_police, taille, couleur), y in zip(lignes, Y_TITRE):
        d.text((X0 - 1, y), texte, font=police(nom_police, taille), fill=couleur, anchor="ls")


def corps(d, lignes, couleur):
    for texte, y in zip(lignes, Y_CORPS):
        d.text((X0, y), texte, font=police(OPEN_SANS, 13), fill=couleur, anchor="ls")


def base(fond, nom_logo):
    im = Image.new("RGB", (W, H), fond)
    lg = logo(nom_logo)
    im.paste(lg, (X0, Y_LOGO), lg)
    lisere(ImageDraw.Draw(im))
    return im


# --------------------------------------------------------------------------
# Scènes (contenu du pan, sur toute la hauteur ; la photo est ajoutée au montage)
# --------------------------------------------------------------------------
def scene_podcast():
    im = base(ANTHRACITE, "logo_reserve.png")
    d = ImageDraw.Draw(im)
    etiquette(im, ICONE_CASQUE, "PODCAST", ORANGE)
    titre(d, [("Hervé Gerbi", SERIF, 34, BLANC), ("raconte", SERIF_ITALIQUE, 38, ORANGE)])
    d.rectangle((X0, Y_FILET, W - X0 - 1, Y_FILET + 2), fill=ORANGE)
    corps(d, ["Histoires vraies d’un avocat de victimes"], GRIS_CLAIR)
    return im


def scene_recrutement(t=0.0):
    """t = 0 : accroche du recrutement ; t = 1 : appel à l'action. Entre les deux, le filet rouge
    s'épaissit jusqu'à devenir le bouton, pendant que le texte d'accroche s'efface."""
    fond = base(CREME, "logo.png")
    d = ImageDraw.Draw(fond)
    etiquette(fond, ICONE_GROUPE, "RECRUTEMENT", ROUGE)
    titre(d, [("Avocat associé", SERIF, 34, ENCRE), ("salarié (H/F)", SERIF, 34, ENCRE)])
    avec_corps = fond.copy()
    corps(ImageDraw.Draw(avec_corps), ["Rejoignez un cabinet exclusivement", "dédié à la défense des victimes"],
          TEXTE)
    im = Image.blend(avec_corps, fond, t) if t else avec_corps
    d = ImageDraw.Draw(im)
    e = 1 - (1 - t) ** 3
    d.rectangle((X0, Y_FILET, W - X0 - 1, Y_FILET + 2 + round((H_BOUTON - 3) * e)), fill=ROUGE)
    if t >= 1:
        f = police(POPPINS, 13)
        texte = "Découvrir l’offre"
        fleche = police(ICONES, 17)
        largeur = f.getlength(texte) + 6 + 17
        x = (W - largeur) / 2
        y = Y_FILET + H_BOUTON / 2
        d.text((x, y + 5), texte, font=f, fill=BLANC, anchor="ls")
        d.text((x + largeur - 17, y + 8), chr(ICONE_FLECHE), font=fleche, fill=BLANC, anchor="ls")
    return im


# --------------------------------------------------------------------------
# Montage
# --------------------------------------------------------------------------
PHOTO = photo()
PAN = masque_pan()


def cadre(im):
    ImageDraw.Draw(im).rectangle((0, 0, W - 1, H - 1), outline=CADRE)
    return im


def monter(scene, volet=None, decalage=0):
    """Photo + pan. volet : scène qui monte par-dessus, son bord abaissé de `decalage` pixels."""
    im = PHOTO.copy()
    im.paste(scene, (0, 0), PAN)
    if volet is not None:
        im.paste(volet, (0, 0), masque_pan(decalage))
    return cadre(im)


def images_animation():
    """Liste de (image RGB, durée en ms) pour un cycle de 10 s."""
    a, b, c = scene_podcast(), scene_recrutement(0), scene_recrutement(1)
    images = [(monter(a), 2700)]
    course = H - PAN_DROITE
    for k in (1, 2, 3, 4):                                  # volet crème montant (ease-out)
        e = 1 - (1 - k / 5) ** 3
        images.append((monter(a, b, round(course * (1 - e))), 50))
    images.append((monter(b), 3100))
    for k in (1, 2, 3):                                     # le filet devient bouton
        images.append((monter(scene_recrutement(k / 4)), 60))
    images.append((monter(c), 10000 - sum(d for _, d in images)))
    return images


def palette(couleurs):
    """Image « P » portant la palette donnée, complétée en répétant sa dernière couleur."""
    pal = Image.new("P", (1, 1))
    pal.putpalette(couleurs + couleurs[-3:] * (256 - len(couleurs) // 3))
    return pal


def palettes(images, couleurs_photo=196):
    """Palette de la photo (entrées 0 à couleurs_photo - 1), puis celle des aplats et du texte lissé.
    Renvoie (palette de la photo seule, palette complète)."""
    haut = cadre(PHOTO.copy()).crop((0, 0, W, PAN_GAUCHE))
    p_photo = haut.quantize(couleurs_photo, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * couleurs_photo]
    pan = np.array(PAN) > 0
    pixels = np.concatenate([np.array(im)[pan] for im, _ in images])
    pile = Image.fromarray(pixels.reshape(-1, 1, 3))
    reste = 256 - couleurs_photo
    p_pan = pile.quantize(reste, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * reste]
    return palette(p_photo), palette(p_photo + p_pan)


def enregistrer_gif(images, chemin):
    pal_photo, pal = palettes(images)
    # Photo tramée une seule fois, sur ses seules couleurs (pas de points orange ou verts du pan) :
    # ses pixels gardent les mêmes index sur toutes les images
    photo_idx = np.array(cadre(PHOTO.copy()).quantize(palette=pal_photo, dither=Image.Dither.FLOYDSTEINBERG))
    hors_pan = np.array(PAN) == 0
    hors_pan[0, :] = hors_pan[-1, :] = hors_pan[:, 0] = hors_pan[:, -1] = True
    cadres = []
    for im, _ in images:
        idx = np.array(im.quantize(palette=pal, dither=Image.Dither.NONE))
        idx = np.where(hors_pan, photo_idx, idx).astype(np.uint8)
        p = Image.fromarray(idx, "P")
        p.putpalette(pal.getpalette())
        cadres.append(p)
    # loop=2 : 2 répétitions après la première lecture, soit 3 lectures (30 s)
    cadres[0].save(chemin, save_all=True, append_images=cadres[1:], duration=[d for _, d in images],
                   loop=2, optimize=False, disposal=1)


def verifier(chemin):
    poids = os.path.getsize(chemin)
    statut = "OK" if poids <= POIDS_MAX else "TROP LOURD"
    print(f"{os.path.basename(chemin)} : {poids / 1000:.0f} Ko ({statut})")
    return poids <= POIDS_MAX


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    images = images_animation()
    gif = os.path.join(SORTIE, "Banniere_300x600_animee.gif")
    jpg = os.path.join(SORTIE, "Banniere_300x600_fixe.jpg")
    enregistrer_gif(images, gif)
    images[-1][0].save(jpg, quality=90, subsampling=0, optimize=True, progressive=True)
    ok = verifier(gif) & verifier(jpg)
    sys.exit(0 if ok else 1)
