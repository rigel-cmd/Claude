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
clair, avec une zone claire de 12 px (3 modules) tout autour. Leurs couleurs figurent telles quelles dans
la palette du GIF et ne sont jamais tramées.

La photo reste identique d'une image à l'autre (mêmes index de palette) : seuls le pan, le pied et la
flèche de la légende changent, ce qui garde le GIF léger. Le script échoue si un fichier dépasse 150 Ko, si
le GIF relu ne redonne pas exactement les images calculées, si la zone claire d'un QR code est encombrée
ou si le pan s'approche à moins de 14 px du visage.
"""

import functools
import os
import sys

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
POLICES = sys.argv[1]
SORTIE = sys.argv[2] if len(sys.argv) > 2 else ICI
RESSOURCES = os.path.join(ICI, "ressources")
POIDS_MAX = 150_000            # 150 Ko, au sens strict (150 000 octets)

URL_OFFRE = "https://www.victimesetprejudices.fr/recrutements/avocat-associe-salarie/"
URL_PODCAST = "https://www.victimesetprejudices.fr/podcast/"

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

# Couleurs relevées sur la 4e de couverture
CREME = (244, 240, 231)
ANTHRACITE = (51, 51, 51)
ROUGE = (181, 32, 38)
ORANGE = (252, 175, 25)
ORANGE_TEXTE = (140, 88, 0)           # orange foncé, pour du texte sur crème (contraste 5,3:1)
VERT = (142, 195, 63)
ENCRE = (21, 31, 36)
BLANC = (255, 255, 255)
GRIS_CLAIR = (232, 232, 232)
CADRE = (196, 190, 178)
COULEURS_EXACTES = [CREME, ANTHRACITE, ROUGE, ORANGE, ORANGE_TEXTE, VERT, ENCRE, BLANC, GRIS_CLAIR, CADRE]

ICONE_CASQUE, ICONE_GROUPE, ICONE_ESSOR, ICONE_RETOUR = 0xF01F, 0xF233, 0xE8E5, 0xE5C4

# Contour du visage, barbe comprise, relevé sur la photo ramenée à 300 px de large (avant rognage) :
# le pan ne doit pas s'en approcher à moins de MARGE_VISAGE px
CONTOUR_VISAGE = [(35, 185), (60, 110), (120, 88), (190, 100), (225, 170), (232, 250), (200, 255),
                  (185, 290), (170, 305), (150, 332), (125, 346), (100, 346), (75, 335), (55, 315),
                  (36, 265)]
MARGE_VISAGE = 14


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
OPEN_SANS_DEMI = "OpenSans_600SemiBold.ttf"
ICONES = "MaterialIcons-Regular.ttf"


# --------------------------------------------------------------------------
# Éléments fixes
# --------------------------------------------------------------------------
def masque_pan(decalage=0, bas=H, k=4):
    """Pan coupé, lissé par suréchantillonnage. decalage > 0 abaisse le bord (volet montant) ;
    bas : le masque s'arrête au-dessus de cette ligne."""
    m = Image.new("L", (W * k, H * k), 0)
    ImageDraw.Draw(m).polygon(
        [(0, (PAN_GAUCHE + decalage) * k), (W * k, (PAN_DROITE + decalage) * k), (W * k, bas * k), (0, bas * k)],
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
def logo():
    im = Image.open(os.path.join(RESSOURCES, "logo.png")).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((LARGEUR_LOGO, round(im.height * LARGEUR_LOGO / im.width)), Image.LANCZOS)


def lisere(d):
    y = H - H_LISERE
    d.rectangle((0, y, round(W * 0.55) - 1, H), fill=ROUGE)
    d.rectangle((round(W * 0.55), y, round(W * 0.82) - 1, H), fill=ORANGE)
    d.rectangle((round(W * 0.82), y, W, H), fill=VERT)


def texte_lisse(im, x, y, texte, nom_police, taille, couleur, approche=0.0, k=4):
    """Texte tracé 4 fois plus grand puis réduit (x, y : début de la ligne de base). Au pixel près,
    l'approche des lettres de Poppins serait irrégulière (« Scan nez », « R ECRUTEMENT »).
    approche : espacement ajouté entre les lettres, en pixels (capitales espacées des étiquettes)."""
    f = police(nom_police, taille * k)
    haut = 2 * taille
    masque = Image.new("L", (W * k, 3 * taille * k), 0)
    d = ImageDraw.Draw(masque)
    xk = x * k
    for morceau in (texte if approche else [texte]):
        d.text((xk, haut * k), morceau, font=f, fill=255, anchor="ls")
        xk += f.getlength(morceau) + approche * k
    im.paste(couleur, (0, round(y) - haut), masque.resize((W, 3 * taille), Image.LANCZOS))


def etiquette(im, code, texte, couleur):
    """Pictogramme et capitales espacées, comme sur la 4e de couverture. Le pictogramme est centré sur la
    hauteur des capitales, d'après l'encre du glyphe."""
    f = police(ICONES, 22)
    g, h, d, b = f.getbbox(chr(code), anchor="ls")
    _, haut, _, bas = police(POPPINS, 11).getbbox("E", anchor="ls")
    milieu_capitales = Y_ETIQUETTE + (haut + bas) / 2
    ImageDraw.Draw(im).text((X0 - g, round(milieu_capitales - (h + b) / 2)), chr(code), font=f, fill=couleur,
                            anchor="ls")
    texte_lisse(im, X0 + d - g + 7, Y_ETIQUETTE, texte, POPPINS, 11, couleur, approche=1.7)


def titre(d, lignes):
    for (texte, nom_police, taille, couleur), y in zip(lignes, Y_TITRE):
        d.text((X0 - 1, y), texte, font=police(nom_police, taille), fill=couleur, anchor="ls")


@functools.lru_cache(maxsize=None)
def matrice_qr(url):
    """Modules du QR code (sans marge), en correction L : version 4 pour l'offre, 3 pour le podcast."""
    qr = segno.make_qr(url, error="L", boost_error=False)
    return tuple(tuple(bool(v) for v in ligne) for ligne in qr.matrix)


def position_qr(url):
    """Coin haut gauche des modules : le QR code du podcast (plus petit) est centré sur celui de l'offre."""
    cote = len(matrice_qr(url)) * MODULE
    return X_QR + (COTE_QR - cote) // 2, Y_QR + (COTE_QR - cote) // 2, cote


def dessiner_qr(d, url, couleur):
    """Modules foncés de MODULE px, au pixel près, sur le fond clair déjà en place."""
    x, y, _ = position_qr(url)
    for i, ligne in enumerate(matrice_qr(url)):
        for j, fonce in enumerate(ligne):
            if fonce:
                d.rectangle((x + j * MODULE, y + i * MODULE, x + (j + 1) * MODULE - 1, y + (i + 1) * MODULE - 1),
                            fill=couleur)


Y_LEGENDE = (Y_QR + 26, Y_QR + 45)    # lignes de base de « Scannez » et de la suite


def pied(im, url, suite, couleur_qr, couleur_verbe, decalage_fleche=0):
    """Pied crème : QR code, flèche et légende sur deux lignes, logo calé sur le bas du QR code.
    decalage_fleche < 0 : la flèche avance vers le QR code."""
    d = ImageDraw.Draw(im)
    d.rectangle((0, Y_PIED, W, H - H_LISERE - 1), fill=CREME)
    dessiner_qr(d, url, couleur_qr)
    d.text((X_COLONNE + decalage_fleche, Y_LEGENDE[0] + 3), chr(ICONE_RETOUR), font=police(ICONES, 20),
           fill=couleur_verbe, anchor="ls")
    texte_lisse(im, X_COLONNE + 22, Y_LEGENDE[0], "Scannez", POPPINS, 16, couleur_verbe)
    texte_lisse(im, X_COLONNE + 22, Y_LEGENDE[1], suite, POPPINS, 12, ENCRE)
    lg = logo()
    im.paste(lg, (X_COLONNE, Y_QR + COTE_QR - lg.height), lg)
    lisere(d)


# --------------------------------------------------------------------------
# Scènes (contenu du pan et du pied, sur toute la hauteur ; la photo est ajoutée au montage)
# --------------------------------------------------------------------------
def scene_offre(decalage_fleche=0):
    im = Image.new("RGB", (W, H), CREME)
    d = ImageDraw.Draw(im)
    etiquette(im, ICONE_GROUPE, "RECRUTEMENT · GRENOBLE", ROUGE)
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
    etiquette(im, ICONE_CASQUE, "PODCAST", ORANGE)
    titre(d, [("Hervé Gerbi", SERIF, 32, BLANC), ("raconte", SERIF_ITALIQUE, 34, ORANGE)])
    d.rectangle((X0, Y_FILET, X1 - 1, Y_FILET + 2), fill=ORANGE)
    d.text((X0, Y_ARGUMENT), "Histoires vraies d’un avocat de victimes", font=police(OPEN_SANS, 13),
           fill=GRIS_CLAIR, anchor="ls")
    pied(im, URL_PODCAST, "pour écouter", ENCRE, ORANGE_TEXTE)
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


# --------------------------------------------------------------------------
# Contrôles
# --------------------------------------------------------------------------
def controler_visage():
    """Vérifie que le bord du pan reste à au moins MARGE_VISAGE px (distance euclidienne) du visage."""
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(x, y - DECALAGE_PHOTO) for x, y in CONTOUR_VISAGE], fill=255)
    visage = np.argwhere(np.array(m) > 0)
    pan = np.array(PAN) > 0
    bord = np.array([(pan[:, x].argmax(), x) for x in range(W)])     # premier pixel du pan, colonne par colonne
    distance = np.sqrt(((bord[:, None, :] - visage[None, :, :]) ** 2).sum(2)).min()
    if distance < MARGE_VISAGE:
        print(f"Le pan s'approche à {distance:.1f} px du visage (minimum : {MARGE_VISAGE} px)")
    return distance >= MARGE_VISAGE


def controler_zone_claire(im, url, nom):
    """Les modules du QR code et leur zone claire de ZONE_CLAIRE px ne contiennent que deux couleurs :
    celle des modules et le crème."""
    x, y, cote = position_qr(url)
    a = np.asarray(im)[y - ZONE_CLAIRE:y + cote + ZONE_CLAIRE, x - ZONE_CLAIRE:x + cote + ZONE_CLAIRE]
    clair = (a == CREME).all(2)
    zone = np.ones(clair.shape, bool)
    zone[ZONE_CLAIRE:-ZONE_CLAIRE, ZONE_CLAIRE:-ZONE_CLAIRE] = False
    couleurs = {tuple(c) for c in a[~clair].reshape(-1, 3)}
    ok = clair[zone].all() and len(couleurs) == 1
    if not ok:
        print(f"QR code {nom} : zone claire encombrée ou modules de plusieurs couleurs")
    return ok


# --------------------------------------------------------------------------
# GIF : palette commune, photo tramée une fois, couleurs de la charte exactes
# --------------------------------------------------------------------------
def palette(couleurs):
    """Image « P » portant la palette donnée, complétée en répétant sa dernière couleur."""
    pal = Image.new("P", (1, 1))
    pal.putpalette(couleurs + couleurs[-3:] * (256 - len(couleurs) // 3))
    return pal


TRANSPARENT = 255           # entrée de palette réservée aux pixels inchangés d'une image à la suivante


def palettes(images, couleurs_photo=190):
    """Palette de la photo (entrées 0 à couleurs_photo - 1), puis les couleurs exactes de la charte
    (aplats, QR codes), puis celles du texte lissé et du logo ; la dernière entrée est réservée à la
    transparence. Renvoie (palette de la photo seule, tableau des 256 couleurs, toutes distinctes)."""
    # Octree plutôt que median cut pour la photo : les petites zones colorées, comme le bleu des iris,
    # gardent leur couleur
    visible = np.array(PAN) == 0
    pixels_photo = np.array(PHOTO)[visible]
    p_photo = (Image.fromarray(pixels_photo.reshape(-1, 1, 3))
               .quantize(couleurs_photo, method=Image.Quantize.FASTOCTREE).getpalette()[:3 * couleurs_photo])
    pixels = np.concatenate([np.array(im)[~visible] for im, _, _ in images])
    exactes = np.array(COULEURS_EXACTES)
    hors_charte = ~(pixels[:, None, :] == exactes[None, :, :]).all(2).any(1)
    reste = 255 - couleurs_photo - len(COULEURS_EXACTES)
    pile = Image.fromarray(pixels[hors_charte].reshape(-1, 1, 3))
    p_reste = pile.quantize(reste, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * reste]
    liste = [tuple(c) for c in np.array(p_photo + [c for rgb in COULEURS_EXACTES for c in rgb] + p_reste)
             .reshape(-1, 3).tolist()]
    # Une couleur en double ferait renuméroter la palette par Pillow : les doublons (et l'entrée de la
    # transparence) reçoivent des couleurs inutilisées
    vues, libres = set(), ((0, 1, k) for k in range(256))
    for i, c in enumerate(liste + [None]):
        if c is None or c in vues:
            c = next(x for x in libres if x not in vues)
            if i < len(liste):
                liste[i] = c
            else:
                liste.append(c)
        vues.add(c)
    return palette(p_photo), np.array(liste)


def indexer(im, couleurs):
    """Index de la couleur la plus proche, calculée exactement (sans trame) : une couleur présente dans
    la palette garde sa valeur exacte, ce qui préserve les aplats et les modules des QR codes."""
    a = np.array(im).reshape(-1, 3).astype(np.int32)
    cle = (a[:, 0] << 16) | (a[:, 1] << 8) | a[:, 2]
    uniques, inverse = np.unique(cle, return_inverse=True)
    rgb = np.stack([uniques >> 16, (uniques >> 8) & 255, uniques & 255], 1)
    ecart = ((rgb[:, None, :] - couleurs[None, :TRANSPARENT, :].astype(np.int32)) ** 2).sum(2)
    return ecart.argmin(1)[inverse].reshape(H, W).astype(np.uint8)


def premiere_image_opaque(chemin):
    """Retire l'indicateur de transparence de la première image (elle n'a aucun pixel transparent) :
    certains outils de contrôle des régies le signalent."""
    octets = bytearray(open(chemin, "rb").read())
    i = 13 + ((3 << ((octets[10] & 7) + 1)) if octets[10] & 0x80 else 0)   # après la palette globale
    while octets[i] == 0x21:                               # extensions qui précèdent la première image
        if octets[i + 1] == 0xF9:
            octets[i + 3] &= 0xFE
            break
        i += 2
        while octets[i]:
            i += octets[i] + 1
        i += 1
    open(chemin, "wb").write(octets)


def enregistrer_gif(images, chemin):
    pal_photo, couleurs = palettes(images)
    # Photo tramée une seule fois, sur ses seules couleurs : ses pixels gardent les mêmes index sur
    # toutes les images
    photo_idx = np.array(PHOTO.quantize(palette=pal_photo, dither=Image.Dither.FLOYDSTEINBERG))
    visible = np.array(PAN) == 0
    bord = np.zeros((H, W), bool)
    bord[0, :] = bord[-1, :] = bord[:, 0] = bord[:, -1] = True
    index_cadre = int(np.flatnonzero((couleurs == CADRE).all(1))[0])
    octets = bytes(couleurs.astype(np.uint8).flatten().tolist())
    cadres = []
    for im, _, _ in images:
        idx = np.where(visible, photo_idx, indexer(im, couleurs))
        idx[bord] = index_cadre                            # filet du cadre d'une couleur exacte, sans trame
        p = Image.fromarray(idx.astype(np.uint8), "P")
        p.putpalette(octets)
        cadres.append(p)
    # Palette globale imposée (aucune renumérotation) ; optimize : dans le rectangle qui change d'une
    # image à la suivante, Pillow remplace les pixels inchangés par l'entrée transparente, qui se
    # compresse mieux. loop=2 : 2 répétitions après la première lecture, soit 3 lectures
    cadres[0].save(chemin, format="GIF", save_all=True, append_images=cadres[1:],
                   duration=[d for _, d, _ in images], loop=2, palette=octets, optimize=True,
                   transparency=TRANSPARENT, disposal=1)
    premiere_image_opaque(chemin)
    return cadres


def relire_gif(chemin, cadres):
    """Le GIF relu doit redonner exactement chaque image (couleurs des QR codes comprises)."""
    relu = Image.open(chemin)
    ok = relu.n_frames == len(cadres)
    for i, attendu in enumerate(cadres):
        relu.seek(min(i, relu.n_frames - 1))
        ok &= relu.convert("RGB").tobytes() == attendu.convert("RGB").tobytes()
    if not ok:
        print(f"{os.path.basename(chemin).removesuffix('.tmp')} : les images relues diffèrent des images calculées")
    return ok


def verifier(chemin):
    poids = os.path.getsize(chemin)
    statut = "OK" if poids <= POIDS_MAX else "TROP LOURD"
    print(f"{os.path.basename(chemin).removesuffix('.tmp')} : {poids / 1000:.0f} Ko ({statut})")
    return poids <= POIDS_MAX


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    images = images_animation()
    gif = os.path.join(SORTIE, "Banniere_300x600_animee.gif")
    jpg = os.path.join(SORTIE, "Banniere_300x600_fixe.jpg")
    # Fichiers écrits sous un nom provisoire : ils ne remplacent les livrables que si tous les contrôles
    # passent
    gif_tmp, jpg_tmp = gif + ".tmp", jpg + ".tmp"
    cadres = enregistrer_gif(images, gif_tmp)
    images[-1][0].save(jpg_tmp, format="JPEG", quality=92, subsampling=0, optimize=True)
    ok = verifier(gif_tmp) & verifier(jpg_tmp) & relire_gif(gif_tmp, cadres) & controler_visage()
    for i, ((_, _, url), cadre_gif) in enumerate(zip(images, cadres)):
        ok &= controler_zone_claire(cadre_gif.convert("RGB"), url, f"de l'image {i} du GIF")
    if ok:
        os.replace(gif_tmp, gif)
        os.replace(jpg_tmp, jpg)
    else:
        os.remove(gif_tmp)
        os.remove(jpg_tmp)
        print("Contrôles en échec : les fichiers précédents sont conservés")
    sys.exit(0 if ok else 1)
