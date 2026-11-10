"""Éléments communs aux bannières de la campagne Gazette du Palais 2026 (300 × 600 et 600 × 200 px) :
charte, polices, texte lissé, QR codes, contrôles, et écriture des livrables (GIF animé et JPEG fixe).

Le GIF repose sur une palette commune à toutes les images : la photo y est tramée une seule fois et garde
les mêmes index d'une image à l'autre ; les couleurs de la charte (aplats, QR codes) y figurent telles
quelles et ne sont jamais tramées. Seuls les pixels qui changent pèsent dans les images suivantes, ce qui
garde le fichier léger.
"""

import functools
import os

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RESSOURCES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ressources")
POIDS_MAX = 150_000            # 150 Ko, au sens strict (150 000 octets)

URL_OFFRE = "https://www.victimesetprejudices.fr/recrutements/avocat-associe-salarie/"
URL_PODCAST = "https://www.victimesetprejudices.fr/podcast/"

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
ICONE_HAUT = 0xE5D8                   # flèche vers le haut

SERIF = "DMSerifDisplay_400Regular.ttf"
SERIF_ITALIQUE = "DMSerifDisplay_400Regular_Italic.ttf"
POPPINS = "Poppins_600SemiBold.ttf"
OPEN_SANS = "OpenSans_400Regular.ttf"
OPEN_SANS_DEMI = "OpenSans_600SemiBold.ttf"
ICONES = "MaterialIcons-Regular.ttf"

# Portrait : ressources/photo_herve_gerbi.jpg reprend la 4e de couverture de x = 404 à 866 et de y = 0 à 640
# (en unités de la page, large de 866), à 1,36 px par unité. À gauche de x = 404 commence le texte du
# podcast ; la bande de 404 à 425 est le fond sombre de la photo, sans texte.
# Contour du visage, barbe comprise, relevé sur la partie x >= 425 de la ressource (DECALAGE_RESSOURCE px
# plus à droite), ramenée à 300 px de large
DECALAGE_RESSOURCE = 29
CONTOUR_VISAGE = [(35, 185), (60, 110), (120, 88), (190, 100), (225, 170), (232, 250), (200, 255),
                  (185, 290), (170, 305), (150, 332), (125, 346), (100, 346), (75, 335), (55, 315),
                  (36, 265)]

_POLICES = []


def utiliser_polices(dossier):
    """Dossier parcouru récursivement (un node_modules, par exemple) qui contient les polices."""
    _POLICES[:] = [dossier]


@functools.lru_cache(maxsize=None)
def chemin_police(nom):
    for racine, _, fichiers in os.walk(_POLICES[0]):
        if nom in fichiers:
            return os.path.join(racine, nom)
    raise SystemExit(f"Police introuvable dans {_POLICES[0]} : {nom}")


@functools.lru_cache(maxsize=None)
def police(nom, taille):
    return ImageFont.truetype(chemin_police(nom), taille)


# --------------------------------------------------------------------------
# Dessin
# --------------------------------------------------------------------------
def photo(w, h, echelle, dx, dy):
    """Portrait réduit à `echelle` (pixels de bannière par pixel de ressource), décalé de (dx, dy), sur un
    fond de w × h px."""
    im = Image.open(os.path.join(RESSOURCES, "photo_herve_gerbi.jpg")).convert("RGB")
    im = im.resize((round(im.width * echelle), round(im.height * echelle)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=50, threshold=2))
    fond = Image.new("RGB", (w, h), ANTHRACITE)
    fond.paste(im, (-dx, -dy))
    return fond


def contour_visage(echelle, dx, dy):
    """Contour du visage en pixels de la bannière, pour la photo de photo(…, echelle, dx, dy)."""
    return [((2 * x + DECALAGE_RESSOURCE) * echelle - dx, 2 * y * echelle - dy) for x, y in CONTOUR_VISAGE]


def controler_cadrage(echelle, dy, marge):
    """Vérifie que le haut de la chevelure (relevé à y = 45 sur la photo à 300 px) reste à au moins
    `marge` px du haut de la bannière : la tête ne doit pas être coupée."""
    haut = 2 * 45 * echelle - dy
    if haut < marge:
        print(f"La tête est coupée : le haut des cheveux est à {haut:.0f} px du haut (minimum : {marge} px)")
    return haut >= marge


@functools.lru_cache(maxsize=None)
def logo(fichier, largeur):
    im = Image.open(os.path.join(RESSOURCES, fichier)).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((largeur, round(im.height * largeur / im.width)), Image.LANCZOS)


def lisere(d, w, h, hauteur):
    """Liseré tricolore du cabinet, sur toute la largeur, en bas de la bannière."""
    y = h - hauteur
    d.rectangle((0, y, round(w * 0.55) - 1, h), fill=ROUGE)
    d.rectangle((round(w * 0.55), y, round(w * 0.82) - 1, h), fill=ORANGE)
    d.rectangle((round(w * 0.82), y, w, h), fill=VERT)


def cadre(im):
    """Filet gris de 1 px autour de la bannière, pour la détacher des pages blanches des sites."""
    ImageDraw.Draw(im).rectangle((0, 0, im.width - 1, im.height - 1), outline=CADRE)
    return im


def texte_lisse(im, x, y, texte, nom_police, taille, couleur, approche=0.0, k=4):
    """Texte tracé 4 fois plus grand puis réduit (x, y : début de la ligne de base). Au pixel près,
    l'approche des lettres de Poppins serait irrégulière (« Scan nez », « R ECRUTEMENT »).
    approche : espacement ajouté entre les lettres, en pixels (capitales espacées des étiquettes)."""
    f = police(nom_police, taille * k)
    haut = 2 * taille
    masque = Image.new("L", (im.width * k, 3 * taille * k), 0)
    d = ImageDraw.Draw(masque)
    xk = x * k
    for morceau in (texte if approche else [texte]):
        d.text((xk, haut * k), morceau, font=f, fill=255, anchor="ls")
        xk += f.getlength(morceau) + approche * k
    im.paste(couleur, (0, round(y) - haut), masque.resize((im.width, 3 * taille), Image.LANCZOS))


def etiquette(im, x, y, code, texte, couleur):
    """Pictogramme et capitales espacées, comme sur la 4e de couverture (y : ligne de base). Le
    pictogramme est centré sur la hauteur des capitales, d'après l'encre du glyphe."""
    f = police(ICONES, 22)
    g, h, d, b = f.getbbox(chr(code), anchor="ls")
    _, haut, _, bas = police(POPPINS, 11).getbbox("E", anchor="ls")
    milieu_capitales = y + (haut + bas) / 2
    ImageDraw.Draw(im).text((x - g, round(milieu_capitales - (h + b) / 2)), chr(code), font=f, fill=couleur,
                            anchor="ls")
    texte_lisse(im, x + d - g + 7, y, texte, POPPINS, 11, couleur, approche=1.7)


@functools.lru_cache(maxsize=None)
def matrice_qr(url):
    """Modules du QR code (sans marge), en correction L : version 4 pour l'offre, 3 pour le podcast."""
    qr = segno.make_qr(url, error="L", boost_error=False)
    return tuple(tuple(bool(v) for v in ligne) for ligne in qr.matrix)


def dessiner_qr(d, url, x, y, module, couleur):
    """Modules foncés de `module` px, au pixel près, sur le fond clair déjà en place (x, y : coin haut
    gauche des modules)."""
    for i, ligne in enumerate(matrice_qr(url)):
        for j, fonce in enumerate(ligne):
            if fonce:
                d.rectangle((x + j * module, y + i * module, x + (j + 1) * module - 1, y + (i + 1) * module - 1),
                            fill=couleur)


def masque_lisse(points, w, h, k=4):
    """Polygone lissé par suréchantillonnage (points en pixels de la bannière)."""
    m = Image.new("L", (w * k, h * k), 0)
    ImageDraw.Draw(m).polygon([(x * k, y * k) for x, y in points], fill=255)
    return m.resize((w, h), Image.LANCZOS)


# --------------------------------------------------------------------------
# Contrôles
# --------------------------------------------------------------------------
def controler_visage(pan, contour, marge):
    """Vérifie que le bord du pan reste à au moins `marge` px (distance euclidienne) du visage, dont
    le contour est donné en pixels de la bannière."""
    p = np.array(pan) > 0
    m = Image.new("L", pan.size, 0)
    ImageDraw.Draw(m).polygon(contour, fill=255)
    visage = np.argwhere(np.array(m) > 0)
    # Bord du pan : ses pixels dont un voisin direct est hors du pan (l'extérieur de l'image compte
    # comme pan, pour ne pas prendre les bords de l'image pour celui du pan)
    q = np.pad(p, 1, constant_values=True)
    dehors = ~q[:-2, 1:-1] | ~q[2:, 1:-1] | ~q[1:-1, :-2] | ~q[1:-1, 2:]
    bord = np.argwhere(p & dehors)
    distance = min(float(np.sqrt(((bord[i:i + 2000, None, :] - visage[None, :, :]) ** 2).sum(2)).min())
                   for i in range(0, len(bord), 2000))
    if distance < marge:
        print(f"Le pan s'approche à {distance:.1f} px du visage (minimum : {marge} px)")
    return distance >= marge


def controler_zone_claire(im, x, y, cote, zone, nom):
    """Les modules du QR code et leur zone claire de `zone` px ne contiennent que deux couleurs :
    celle des modules et le crème."""
    a = np.asarray(im)[y - zone:y + cote + zone, x - zone:x + cote + zone]
    clair = (a == CREME).all(2)
    autour = np.ones(clair.shape, bool)
    autour[zone:-zone, zone:-zone] = False
    couleurs = {tuple(c) for c in a[~clair].reshape(-1, 3)}
    ok = a.shape[:2] == (cote + 2 * zone,) * 2 and clair[autour].all() and len(couleurs) == 1
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


def palettes(images, photo, visible, couleurs_photo=190):
    """Palette de la photo (entrées 0 à couleurs_photo - 1), puis les couleurs exactes de la charte
    (aplats, QR codes), puis celles du texte lissé et du logo ; la dernière entrée est réservée à la
    transparence. visible : pixels où la photo apparaît. Renvoie (palette de la photo seule, tableau des
    256 couleurs, toutes distinctes)."""
    # Octree plutôt que median cut pour la photo : les petites zones colorées, comme le bleu des iris,
    # gardent leur couleur
    pixels_photo = np.array(photo)[visible]
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
    return ecart.argmin(1)[inverse].reshape(im.height, im.width).astype(np.uint8)


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


def enregistrer_gif(images, chemin, photo, visible):
    """images : liste de (image RGB, durée en ms, adresse du QR code affiché). Renvoie les images « P »."""
    pal_photo, couleurs = palettes(images, photo, visible)
    # Photo tramée une seule fois, sur ses seules couleurs : ses pixels gardent les mêmes index sur
    # toutes les images
    photo_idx = np.array(photo.quantize(palette=pal_photo, dither=Image.Dither.FLOYDSTEINBERG))
    h, w = visible.shape
    bord = np.zeros((h, w), bool)
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


def livrer(images, photo, visible, gif, jpg, controles, controle_image):
    """Écrit le GIF et le JPEG (la dernière image) sous un nom provisoire, les contrôle, puis remplace
    les livrables seulement si tout passe. controles : contrôles indépendants des images (fonctions) ;
    controle_image(image RGB, adresse du QR code, nom) : contrôle appliqué à chaque image du GIF relu."""
    gif_tmp, jpg_tmp = gif + ".tmp", jpg + ".tmp"
    cadres = enregistrer_gif(images, gif_tmp, photo, visible)
    images[-1][0].save(jpg_tmp, format="JPEG", quality=92, subsampling=0, optimize=True)
    ok = verifier(gif_tmp) & verifier(jpg_tmp) & relire_gif(gif_tmp, cadres)
    for c in controles:
        ok &= c()
    for i, ((_, _, url), cadre_gif) in enumerate(zip(images, cadres)):
        ok &= controle_image(cadre_gif.convert("RGB"), url, f"de l'image {i} du GIF")
    if ok:
        os.replace(gif_tmp, gif)
        os.replace(jpg_tmp, jpg)
    else:
        os.remove(gif_tmp)
        os.remove(jpg_tmp)
        print("Contrôles en échec : les fichiers précédents sont conservés")
    return ok
