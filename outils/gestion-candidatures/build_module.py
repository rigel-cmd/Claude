# -*- coding: utf-8 -*-
"""
Produit les deux formes livrables du module VBA à partir de la source UTF-8.

  VP_Candidatures.bas            -> Fichier ▸ Importer un fichier (garde Attribute VB_Name)
  VP_Candidatures_a_coller.txt   -> Insertion ▸ Module puis copier-coller (sans Attribute)

Deux contraintes de l'éditeur VBA, vérifiées ici :
  * encodage Windows-1252 (l'UTF-8 rend les accents illisibles) ;
  * fins de ligne CRLF (avec des LF seuls, l'import échoue).
"""
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "VP_Candidatures.utf8.bas"
src = open(SRC, encoding="utf-8").read().replace("\r\n", "\n").replace("\r", "\n")
if not src.endswith("\n"):
    src += "\n"
lignes = src.split("\n")
if not lignes[0].startswith("Attribute VB_Name"):
    sys.exit("La première ligne doit être « Attribute VB_Name = ... »")

open("VP_Candidatures.bas", "wb").write("\r\n".join(lignes).encode("cp1252"))
open("VP_Candidatures_a_coller.txt", "wb").write(
    ("' Module VP_Candidatures - a coller dans un module standard\r\n"
     "' (Alt+F11 > Insertion > Module, puis Ctrl+A / Ctrl+V dans la fenetre de droite)\r\n"
     + "\r\n".join(lignes[1:])).encode("cp1252"))

for f in ("VP_Candidatures.bas", "VP_Candidatures_a_coller.txt"):
    b = open(f, "rb").read()
    txt = b.decode("cp1252")
    assert b.count(b"\n") == b.count(b"\r\n") == b.count(b"\r"), "%s : fins de ligne incohérentes" % f
    trop = [i for i, l in enumerate(txt.splitlines(), 1) if len(l) > 1000]
    assert not trop, "%s : ligne(s) de plus de 1000 caractères %s" % (f, trop)
    print("OK %-32s %6d octets, %d lignes CRLF" % (f, len(b), b.count(b"\r\n")))
