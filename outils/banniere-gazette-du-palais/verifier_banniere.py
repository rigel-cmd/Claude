"""Contrôle d'une bannière 300 x 600 (GIF animé + JPEG fixe).

Usage : python3 -I verifier_banniere.py <banniere.gif> <banniere.jpg> <dossier_rapport> [url_attendue ...]

Vérifie : dimensions, poids (<= 150 000 octets), boucle et durée totale (<= 30 s), concordance de la
dernière image du GIF avec le JPEG, et la lecture des QR codes sur chaque image distincte, à l'échelle 1
et dans trois simulations de prise de vue au téléphone (flou, rotation, reflet, distance).
Produit dans <dossier_rapport> : planche.png (scènes tenues >= 1 s, à l'échelle 1), final_x2.png
(dernière image agrandie 2 fois, pixels nets) et rapport.json.
"""
import json, os, sys
import numpy as np
import zxingcpp
from PIL import Image, ImageEnhance, ImageFilter, ImageSequence

gif_p, jpg_p, out = sys.argv[1:4]
attendues = sys.argv[4:]
os.makedirs(out, exist_ok=True)
rep = {"erreurs": []}

def err(m):
    rep["erreurs"].append(m)

for p in (gif_p, jpg_p):
    n = os.path.getsize(p)
    rep[f"poids_{os.path.basename(p)}"] = n
    if n > 150_000:
        err(f"{os.path.basename(p)} pèse {n} octets (> 150 000)")
    im = Image.open(p)
    if im.size != (300, 600):
        err(f"{os.path.basename(p)} mesure {im.size}")

g = Image.open(gif_p)
images, durees = [], []
for f in ImageSequence.Iterator(g):
    images.append(f.convert("RGB"))
    durees.append(f.info.get("duration", 0))
boucle = g.info.get("loop")
cycle = sum(durees)
lectures = None if boucle in (None, 0) else boucle + 1
rep.update(nb_images=len(images), durees_ms=durees, cycle_ms=cycle, loop=boucle,
           lectures=lectures, duree_totale_s=None if lectures is None else cycle * lectures / 1000)
if lectures is None:
    err("le GIF boucle à l'infini ou n'a pas de boucle (attendu : arrêt après 30 s maximum)")
elif cycle * lectures > 30_000:
    err(f"durée totale {cycle * lectures / 1000:.1f} s > 30 s")

jpg = Image.open(jpg_p).convert("RGB")
ecart = float(np.abs(np.asarray(images[-1], float) - np.asarray(jpg, float)).mean())
rep["ecart_moyen_dernier_cadre_vs_jpeg"] = round(ecart, 2)
if ecart > 6:
    err(f"le JPEG ne correspond pas à la dernière image du GIF (écart moyen {ecart:.1f})")

def simulations(im):
    yield "ecran_1x", im
    a = im.resize((750, 1500), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.6))
    bruit = np.clip(np.asarray(a, float) + np.random.default_rng(1).normal(0, 6, (1500, 750, 3)), 0, 255)
    yield "photo_floue_bruitee", Image.fromarray(bruit.astype(np.uint8))
    b = im.resize((480, 960), Image.BILINEAR).rotate(5, Image.BILINEAR, expand=True, fillcolor=(30, 30, 30))
    b = Image.blend(b, Image.new("RGB", b.size, "white"), 0.28).filter(ImageFilter.GaussianBlur(0.9))
    yield "rotation_reflet", b
    c = im.resize((195, 390), Image.LANCZOS).resize((585, 1170), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.0))
    yield "distance_x0.65", c

def simulations_exigeantes(im):
    """Conditions dures, pour mesurer la marge de lecture (non bloquantes)."""
    a = im.resize((135, 270), Image.LANCZOS).resize((540, 1080), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    yield "distance_x0.45", a
    b = im.resize((750, 1500), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3.2))
    yield "flou_fort", b
    c = Image.blend(im, Image.new("RGB", im.size, "white"), 0.5).resize((600, 1200), Image.BILINEAR)
    yield "contraste_faible_x0.5", Image.blend(c, Image.new("RGB", c.size, "white"), 0.0).filter(ImageFilter.GaussianBlur(1.4))

def lire(im):
    return sorted({r.text for r in zxingcpp.read_barcodes(im)})

vus, distincts = {}, []
for i, im in enumerate(images):
    cle = im.tobytes()
    if cle in vus:
        continue
    vus[cle] = i
    distincts.append(i)
qr = {}
for i in distincts:
    qr[i] = {nom: lire(v) for nom, v in simulations(images[i])}
rep["qr_par_image"] = {str(i): {"duree_ms": durees[i], **qr[i]} for i in distincts}

for url in attendues:
    tenues = [i for i in distincts if durees[i] >= 1000 and url in qr[i]["ecran_1x"]]
    robustes = [i for i in tenues if all(url in v for v in qr[i].values())]
    rep[f"url {url}"] = {"images_tenues_lisibles_1x": tenues, "images_lisibles_dans_toutes_simulations": robustes}
    if not robustes:
        err(f"QR {url} : illisible dans au moins une simulation sur toutes les images tenues")
derniere = qr[distincts[-1]] if distincts[-1] == len(images) - 1 else qr[vus[images[-1].tobytes()]]
rep["qr_derniere_image"] = derniere
rep["qr_jpeg"] = {nom: lire(v) for nom, v in simulations(jpg)}
rep["qr_jpeg_conditions_dures"] = {nom: lire(v) for nom, v in simulations_exigeantes(jpg)}
rep["marge_qr_jpeg"] = {u: sum(u in v for v in rep["qr_jpeg_conditions_dures"].values()) for u in attendues}
for url in attendues[:1]:
    if not all(url in v for v in rep["qr_jpeg"].values()):
        err(f"QR {url} : pas lisible dans toutes les simulations sur le JPEG")

tenues = [i for i in range(len(images)) if durees[i] >= 1000] or [len(images) - 1]
pl = Image.new("RGB", (310 * len(tenues), 600), "white")
for k, i in enumerate(tenues):
    pl.paste(images[i], (k * 310, 0))
pl.save(os.path.join(out, "planche.png"))
images[-1].resize((600, 1200), Image.NEAREST).save(os.path.join(out, "final_x2.png"))
with open(os.path.join(out, "rapport.json"), "w") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "qr_par_image"}, ensure_ascii=False, indent=1))
print("OK" if not rep["erreurs"] else "ECHEC")
