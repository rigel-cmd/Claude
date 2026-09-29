"""Version web de l'offre « Avocat(e) associé(e) salarié(e) », à intégrer sur la page Recrutements
du site du cabinet.

Usage : python3 generer_offre_html.py [sortie.html]

Produit un bloc HTML autonome :
- styles embarqués et limités au bloc (sélecteurs préfixés par #vpo-offre) : le thème du site
  n'est pas modifié, et ses styles de titres, paragraphes, listes ou liens ne déforment pas le bloc ;
- mise en page adaptée à la largeur de la zone de contenu (container queries), du mobile au bureau ;
- feuille du logo et pictogrammes en SVG, sans image à téléverser ni script ;
- données structurées JobPosting (schema.org) pour Google Jobs, rédigées à partir du même texte ;
- aucune ligne vide, pour que WordPress n'insère pas de balises <p> parasites.

Les polices Poppins et Open Sans du site sont utilisées si le thème les charge ; sinon, repli sur Arial.
"""

import html
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ICI, "Offre_emploi_avocat_site.html")
DATE_PUBLICATION = "2026-09-29"
EMAIL = "recrutement@victimesetprejudices.fr"
SUJET = "Candidature – Avocat(e) associé(e) salarié(e)"

# ---------------------------------------------------------------------------
# Contenu (identique à la version PDF contrastée)
# ---------------------------------------------------------------------------
TITRE = ("Avocat(e) associé(e)", "salarié(e)")
ACCROCHE = ("Nous recherchons aujourd'hui un(e) avocat(e) démontrant un fort leadership et une capacité "
            "à prendre à terme le relais dans l'animation du cabinet.")
PHRASE_CLE = "Ce poste est créé dans une perspective rapide d'association."
ETIQUETTES = ["Grenoble (38)", "CDI", "Statut cadre", "Perspective d'association"]

CABINET = ("**Victimes & Préjudices Avocats** est un cabinet grenoblois et annecien **exclusivement dédié "
           "à la défense des victimes** : accidents de la route, responsabilité médicale, accidents corporels "
           "et maladies du travail, accidents de la vie, droit pénal des victimes. Nous accompagnons chaque "
           "jour les victimes et leurs familles **jusqu'à leur complète indemnisation**.")
CITATION = ("« Défendre les victimes n'est pas seulement un métier. C'est d'abord notre engagement. »",
            "Hervé Gerbi, avocat fondateur")

MISSIONS = [
    ("Piloter", "un portefeuille de dossiers jusqu'à l'indemnisation définitive"),
    ("Construire", "des stratégies d'indemnisation sur mesure : analyse des pièces médicales et juridiques, "
                   "évaluation et chiffrage des préjudices"),
    ("Rédiger", "les actes : assignations, conclusions, consultations, notes de synthèse"),
    ("Préparer et conduire", "les expertises médicales amiables et judiciaires, en lien étroit avec les "
                             "médecins de recours et les autres experts"),
    ("Plaider", "devant les juridictions civiles, administratives et pénales"),
    ("Porter la relation client", "accompagner les victimes et leurs proches à chaque étape, en interlocuteur "
                                  "ou interlocutrice de référence"),
    ("Développer", "les relations avec les prescripteurs, la visibilité, les relations presse et de nouveaux "
                   "axes de pratique"),
    ("Faire évoluer", "nos méthodes : structuration des process, outils numériques, intelligence artificielle, "
                      "montée en compétence de l'équipe"),
]

FORMATION = [
    ("CAPA", ""),
    ("5 ans minimum", "de pratique en cabinet, avec une réelle exposition au contentieux et à la relation client"),
    ("+ Spécialisation", "en droit du dommage corporel, en droit de la santé ou en corporel du travail serait un plus"),
]
A_DEFAUT = ("**À défaut**, votre capacité à vous approprier rapidement la matière et à prendre le relais "
            "compte davantage qu'une spécialisation déjà acquise.")
COMPETENCES = [
    ("Responsabilité civile :", "solide maîtrise du droit de la responsabilité civile et des mécanismes d'indemnisation."),
    ("Actes et plaidoirie :", "aisance en rédaction d'actes et à la plaidoirie."),
    ("Pièces médicales :", "capacité à travailler sur pièces médicales et à dialoguer avec des experts."),
    ("Numérique et IA :", "appétence réelle pour les outils numériques et l'innovation juridique (digitalisation, IA)."),
]
QUALITES = [
    ("Leadership :", "vous savez entraîner une équipe, arbitrer et décider."),
    ("Esprit entrepreneurial :", "vous prenez des initiatives et vous inscrivez dans une logique de développement."),
    ("Excellente communication :", "à l'écrit comme à l'oral, devant un tribunal comme face à des victimes éprouvées."),
    ("Sens affirmé de la relation client :", "écoute, empathie, humanité."),
    ("Autonomie, rigueur et sens du collectif", ", dans un environnement exigeant et bienveillant."),
]

OFFRE = ("**Vous avancez vers l'association par étapes.** Vous prendrez en charge des responsabilités "
         "progressivement.")
OFFRE_FORTS = [
    ("218 jours", "CDI, statut cadre, forfait annuel ; rémunération fixe selon profil et expérience"),
    ("PEE et PER", "avec abondement du cabinet, en plus des tickets restaurant"),
]
OFFRE_PLUS = [
    ("Fort enjeu humain", "des dossiers techniques, au service exclusif des victimes"),
    ("Taille humaine", "un cabinet équipé d'outils numériques performants et engagé dans l'innovation"),
    ("Au cœur des Alpes", "Grenoble et son cadre de vie montagneux"),
]

REPERES = [
    ("lieu", "rouge", "Lieu", "Grenoble (38)", "Le cabinet est implanté à Grenoble et à Annecy"),
    ("contrat", "orange", "Contrat", "CDI · statut cadre", "Avocat(e) salarié(e), forfait jours (218), association future"),
    ("agenda", "vert", "Recrutement", "4 étapes", "Un échange téléphonique, puis trois entretiens au cabinet"),
]

# ---------------------------------------------------------------------------
# Typographie et balisage
# ---------------------------------------------------------------------------
NBSP = "&nbsp;"


def fmt(texte):
    """Échappe le HTML, applique la typographie française et convertit **gras** en <strong>."""
    s = html.escape(texte, quote=False).replace("'", "’")
    s = re.sub(r" ([:;?!»])", NBSP + r"\1", s)
    s = s.replace("« ", "«" + NBSP)
    s = re.sub(r"(\d) (?=\d|ans|jours|étapes)", r"\1" + NBSP, s)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


with open(os.path.join(ICI, "feuille.svg"), encoding="utf8") as f:
    FEUILLE = f.read().strip().replace(
        '<svg xmlns="http://www.w3.org/2000/svg"',
        '<svg class="vpo-feuille" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"')

# Pictogrammes Material Icons (licence Apache 2.0)
ICONES = {
    "lieu": "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
    "contrat": "M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z",
    "agenda": "M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z",
    "mail": "M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z",
}


def icone(nom):
    return (f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'<path fill="currentColor" d="{ICONES[nom]}"/></svg>')


def vague(classe, d):
    return (f'<svg class="vpo-vague {classe}" viewBox="0 0 1200 48" preserveAspectRatio="none" '
            f'aria-hidden="true" focusable="false"><path d="{d}"/></svg>')


def tuiles(elements, variante):
    lignes = [f'<ul class="vpo-tuiles vpo-tuiles--{variante} vpo-grille-{len(elements)}">']
    for valeur, libelle in elements:
        detail = f'<span class="vpo-tuile-txt">{fmt(libelle)}</span>' if libelle else ""
        lignes.append(f'<li class="vpo-tuile"><span class="vpo-tuile-val">{fmt(valeur)}</span>{detail}</li>')
    lignes.append("</ul>")
    return lignes


def liste_puces(entete, elements):
    lignes = ['<div class="vpo-liste">', f'<p class="vpo-liste-tete">{fmt(entete)}</p>', '<ul class="vpo-puces">']
    lignes += [f"<li><strong>{fmt(g)}</strong> {fmt(r)}</li>" if not r.startswith(",")
               else f"<li><strong>{fmt(g)}</strong>{fmt(r)}</li>" for g, r in elements]
    lignes += ["</ul>", "</div>"]
    return lignes


def section(num, rail, surtitre, titre, contenu):
    ident = f"vpo-s{num}"
    return [
        f'<section class="vpo-sec" aria-labelledby="{ident}">',
        f'<div class="vpo-rail"><span class="vpo-num" aria-hidden="true">0{num}</span>{rail}</div>',
        '<div class="vpo-main">',
        f'<p class="vpo-surtitre">{fmt(surtitre)}</p>',
        f'<h3 class="vpo-h3" id="{ident}">{fmt(titre)}</h3>',
        *contenu,
        "</div>",
        "</section>",
    ]


def question(texte):
    return f'<p class="vpo-question">{fmt(texte)}</p>'


# ---------------------------------------------------------------------------
# Bloc HTML
# ---------------------------------------------------------------------------
mailto = f"mailto:{EMAIL}?subject=" + re.sub(
    r"[^A-Za-z0-9._~-]", lambda m: "".join(f"%{b:02X}" for b in m.group(0).encode("utf8")), SUJET)

corps = [
    '<header class="vpo-hero">',
    FEUILLE,
    '<div class="vpo-hero-in">',
    '<p class="vpo-surtitre vpo-surtitre--orange">Offre d’emploi · CDI</p>',
    f'<h2 class="vpo-titre">{fmt(TITRE[0])} <span>{fmt(TITRE[1])}</span></h2>',
    f'<p class="vpo-accroche">{fmt(ACCROCHE)}</p>',
    f'<p class="vpo-cle">{fmt(PHRASE_CLE)}</p>',
    '<ul class="vpo-etiquettes">',
    *[f"<li>{fmt(e)}</li>" for e in ETIQUETTES[:-1]],
    f'<li class="vpo-accent">{fmt(ETIQUETTES[-1])}</li>',
    "</ul>",
    '<a class="vpo-bouton" href="#vpo-candidater">Comment candidater&nbsp;?</a>',
    "</div>",
    "</header>",
    vague("vpo-vague--bas", "M0 0H1200V20C980 52 720 50 450 30 280 18 120 22 0 40Z"),
    '<div class="vpo-corps">',
    *section(1, f'<figure class="vpo-citation"><blockquote>{fmt(CITATION[0])}</blockquote>'
                f'<figcaption>{fmt(CITATION[1])}</figcaption></figure>',
             "Le cabinet et le contexte", "Un cabinet dédié aux victimes",
             [f'<p class="vpo-texte">{fmt(CABINET)}</p>']),
    *section(2, question("Prêt(e) à relever de nouveaux défis ?"), "Vos missions",
             "De la consultation à l'indemnisation", [
                 '<ul class="vpo-missions">',
                 *[f'<li><strong>{fmt(t)}</strong><span>{fmt(d)}</span></li>' for t, d in MISSIONS],
                 "</ul>",
             ]),
    *section(3, question("Un projet d'association ?"), "Profil recherché", "Formation et expérience", [
        *tuiles(FORMATION, "ardoise"),
        f'<p class="vpo-texte vpo-defaut">{fmt(A_DEFAUT)}</p>',
        '<div class="vpo-listes">',
        *liste_puces("Compétences techniques", COMPETENCES),
        *liste_puces("Qualités personnelles", QUALITES),
        "</div>",
    ]),
    *section(4, question("Une ambition à la hauteur de la vôtre ?"), "Ce que nous vous offrons",
             "Une perspective d'association", [
                 f'<p class="vpo-texte vpo-intro">{fmt(OFFRE)}</p>',
                 *tuiles(OFFRE_FORTS, "rouge"),
                 *tuiles(OFFRE_PLUS, "creme"),
             ]),
    "</div>",
    vague("vpo-vague--haut", "M0 48H1200V14C1000 30 760 44 520 26 330 12 150 4 0 18Z"),
    '<footer class="vpo-candidater" id="vpo-candidater">',
    '<div class="vpo-candidater-haut">',
    "<div>",
    '<p class="vpo-surtitre vpo-surtitre--orange">Informations pratiques</p>',
    '<h3 class="vpo-h3 vpo-h3--blanc">Comment candidater&nbsp;?</h3>',
    '<p class="vpo-engagement"><strong>Nous étudions toutes les candidatures</strong> '
    "et nous nous engageons à répondre à chacune.</p>",
    "</div>",
    f'<a class="vpo-cta" href="{html.escape(mailto)}"><span class="vpo-cta-ico">{icone("mail")}</span>'
    f'<span class="vpo-cta-txt"><span class="vpo-cta-sur">Envoyez CV et lettre de motivation</span>'
    f'<span class="vpo-cta-mail">{EMAIL.replace("@", "@<wbr>")}</span></span></a>',
    "</div>",
    '<ul class="vpo-reperes">',
    *[f'<li><span class="vpo-rep-ico vpo-rep-ico--{c}">{icone(i)}</span><span class="vpo-rep-txt">'
      f'<strong>{fmt(l)}</strong><span class="vpo-rep-val">{fmt(v)}</span><span>{fmt(d)}</span></span></li>'
      for i, c, l, v, d in REPERES],
    "</ul>",
    '<div class="vpo-lisere" aria-hidden="true"></div>',
    "</footer>",
]

CSS = """
#vpo-offre{--vpo-ardoise:#304859;--vpo-rouge:#B52026;--vpo-orange:#FCAF19;--vpo-vert:#8EC33F;--vpo-creme:#FAF0C7;--vpo-texte:#262626;--vpo-second:#3F4A52;--vpo-filet:#D3D9DE;--vpo-pad:20px;--vpo-titres:"Poppins",Arial,Helvetica,sans-serif;container-type:inline-size;display:block;max-width:1140px;margin:0 auto;font-family:"Open Sans",Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:var(--vpo-texte);text-align:left;-webkit-font-smoothing:antialiased}
#vpo-offre *,#vpo-offre *::before,#vpo-offre *::after{box-sizing:border-box}
#vpo-offre h2,#vpo-offre h3,#vpo-offre p,#vpo-offre ul,#vpo-offre li,#vpo-offre figure,#vpo-offre blockquote,#vpo-offre figcaption{margin:0;padding:0;border:0;background:none;box-shadow:none;font-style:normal;text-transform:none;text-decoration:none;text-align:left;text-indent:0;letter-spacing:normal;word-spacing:normal;text-shadow:none;max-width:none;float:none}
#vpo-offre ul{list-style:none}
#vpo-offre li::before,#vpo-offre li::after,#vpo-offre blockquote::before,#vpo-offre blockquote::after{content:none}
#vpo-offre strong{font-weight:600;color:inherit}
#vpo-offre a{color:inherit;text-decoration:none;border:0;box-shadow:none;background-image:none}
#vpo-offre svg{display:block}
#vpo-offre h2,#vpo-offre h3,#vpo-offre .vpo-num,#vpo-offre .vpo-question,#vpo-offre .vpo-citation blockquote,#vpo-offre .vpo-missions strong,#vpo-offre .vpo-tuile-val,#vpo-offre .vpo-cle,#vpo-offre .vpo-bouton,#vpo-offre .vpo-cta-mail,#vpo-offre .vpo-rep-txt strong{font-family:var(--vpo-titres);font-weight:600;line-height:1.25}
#vpo-offre .vpo-surtitre,#vpo-offre .vpo-etiquettes,#vpo-offre .vpo-liste-tete,#vpo-offre .vpo-cta-sur{font-family:var(--vpo-titres);font-weight:500;font-size:12px;line-height:1.4;letter-spacing:.18em;text-transform:uppercase}
#vpo-offre .vpo-surtitre{color:var(--vpo-rouge);margin-bottom:6px}
#vpo-offre .vpo-surtitre--orange{color:var(--vpo-orange)}
#vpo-offre .vpo-hero{position:relative;overflow:hidden;background:var(--vpo-ardoise);color:#fff;border-radius:14px 14px 0 0;padding:100px var(--vpo-pad) 20px}
#vpo-offre .vpo-feuille{position:absolute;top:22px;right:-22px;width:118px;height:auto;pointer-events:none}
#vpo-offre .vpo-hero-in{position:relative;z-index:1}
#vpo-offre .vpo-titre{font-size:32px;line-height:1.12;color:#fff;margin:4px 0 18px}
#vpo-offre .vpo-titre span{color:var(--vpo-orange)}
#vpo-offre .vpo-accroche{font-size:17px;color:#fff;max-width:640px}
#vpo-offre .vpo-cle{font-size:20px;color:var(--vpo-orange);border-left:4px solid var(--vpo-orange);padding-left:14px;margin:18px 0 22px;max-width:600px}
#vpo-offre .vpo-etiquettes{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:26px}
#vpo-offre .vpo-etiquettes li{border:1px solid rgba(250,240,199,.45);color:var(--vpo-creme);border-radius:999px;padding:5px 12px;font-size:11px}
#vpo-offre .vpo-etiquettes li.vpo-accent{border-color:var(--vpo-orange);color:var(--vpo-orange)}
#vpo-offre .vpo-bouton{display:inline-block;background:var(--vpo-orange);color:var(--vpo-ardoise);font-size:15px;padding:12px 22px;border-radius:8px}
#vpo-offre .vpo-vague{width:100%;height:30px;fill:var(--vpo-ardoise)}
#vpo-offre .vpo-vague--bas{margin-top:-1px}
#vpo-offre .vpo-vague--haut{margin-bottom:-1px;margin-top:8px}
#vpo-offre .vpo-corps{padding:0 var(--vpo-pad)}
#vpo-offre .vpo-sec{display:grid;gap:14px;padding:36px 0}
#vpo-offre .vpo-sec+.vpo-sec{border-top:1px solid var(--vpo-filet)}
#vpo-offre .vpo-rail{display:flex;align-items:baseline;gap:14px}
#vpo-offre .vpo-num{font-size:40px;line-height:1;color:var(--vpo-rouge)}
#vpo-offre .vpo-question{font-size:17px;color:var(--vpo-ardoise)}
#vpo-offre .vpo-citation blockquote{font-size:16px;color:var(--vpo-ardoise)}
#vpo-offre .vpo-citation figcaption{font-size:13px;color:var(--vpo-second);margin-top:6px}
#vpo-offre .vpo-h3{font-size:26px;color:var(--vpo-ardoise);margin-bottom:18px}
#vpo-offre .vpo-h3--blanc{color:#fff;margin-bottom:8px}
#vpo-offre .vpo-texte{text-wrap:pretty}
#vpo-offre .vpo-texte strong{color:var(--vpo-ardoise)}
#vpo-offre .vpo-missions,#vpo-offre .vpo-tuiles,#vpo-offre .vpo-listes,#vpo-offre .vpo-reperes{display:grid;gap:12px}
#vpo-offre .vpo-missions li{background:#fff;border:1px solid var(--vpo-filet);border-left:4px solid var(--vpo-rouge);padding:14px 18px 16px}
#vpo-offre .vpo-missions strong{display:block;font-size:17px;color:var(--vpo-ardoise);margin-bottom:4px}
#vpo-offre .vpo-missions span{display:block;font-size:14.5px;line-height:1.55;color:var(--vpo-second)}
#vpo-offre .vpo-tuile{padding:16px 18px 18px}
#vpo-offre .vpo-tuile-val{display:block;font-size:20px}
#vpo-offre .vpo-tuile-txt{display:block;font-size:14px;line-height:1.5;margin-top:4px}
#vpo-offre .vpo-tuiles--ardoise .vpo-tuile{background:var(--vpo-ardoise);color:#fff}
#vpo-offre .vpo-tuiles--ardoise .vpo-tuile-val{color:var(--vpo-orange)}
#vpo-offre .vpo-tuiles--rouge .vpo-tuile{background:var(--vpo-rouge);color:#fff}
#vpo-offre .vpo-tuiles--rouge .vpo-tuile-val{font-size:24px}
#vpo-offre .vpo-tuiles--creme{margin-top:12px}
#vpo-offre .vpo-tuiles--creme .vpo-tuile{background:var(--vpo-creme);color:var(--vpo-second)}
#vpo-offre .vpo-tuiles--creme .vpo-tuile-val{font-size:18px;color:var(--vpo-ardoise)}
#vpo-offre .vpo-defaut{margin:18px 0 22px}
#vpo-offre .vpo-intro{margin-bottom:18px}
#vpo-offre .vpo-listes{gap:16px}
#vpo-offre .vpo-liste{border:1px solid var(--vpo-filet);background:#fff}
#vpo-offre .vpo-liste-tete{background:var(--vpo-ardoise);color:#fff;padding:10px 18px}
#vpo-offre .vpo-puces{padding:14px 18px 8px}
#vpo-offre .vpo-puces li{position:relative;padding-left:18px;margin-bottom:9px;font-size:14.5px;line-height:1.55}
#vpo-offre .vpo-puces li::before{content:"";position:absolute;left:0;top:.55em;width:7px;height:7px;border-radius:50%;background:var(--vpo-rouge)}
#vpo-offre .vpo-candidater{background:var(--vpo-ardoise);color:var(--vpo-creme);border-radius:0 0 14px 14px;overflow:hidden;padding:12px var(--vpo-pad) 0;scroll-margin-top:140px}
#vpo-offre .vpo-candidater-haut{display:grid;gap:22px;align-items:end}
#vpo-offre .vpo-engagement{font-size:15px}
#vpo-offre .vpo-engagement strong{color:#fff}
#vpo-offre .vpo-cta{display:flex;align-items:center;gap:14px;background:var(--vpo-orange);color:var(--vpo-ardoise);padding:16px 20px;border-radius:10px;min-width:0}
#vpo-offre .vpo-cta-ico{flex:none;display:grid;place-items:center;width:42px;height:42px;border-radius:50%;background:var(--vpo-ardoise);color:#fff}
#vpo-offre .vpo-cta-ico svg{width:22px;height:22px}
#vpo-offre .vpo-cta-txt{display:block;min-width:0}
#vpo-offre .vpo-cta-sur{display:block;font-size:10.5px;margin-bottom:2px}
#vpo-offre .vpo-cta-mail{display:block;font-size:16px;overflow-wrap:break-word}
#vpo-offre .vpo-reperes{gap:20px;margin-top:30px;padding-top:26px;border-top:1px solid rgba(255,255,255,.18)}
#vpo-offre .vpo-reperes li{display:grid;grid-template-columns:40px 1fr;gap:14px;align-items:start}
#vpo-offre .vpo-rep-ico{display:grid;place-items:center;width:40px;height:40px;border-radius:50%;color:#fff}
#vpo-offre .vpo-rep-ico svg{width:21px;height:21px}
#vpo-offre .vpo-rep-ico--rouge{background:var(--vpo-rouge)}
#vpo-offre .vpo-rep-ico--orange{background:var(--vpo-orange)}
#vpo-offre .vpo-rep-ico--vert{background:var(--vpo-vert)}
#vpo-offre .vpo-rep-txt{display:block;font-size:14px;line-height:1.5}
#vpo-offre .vpo-rep-txt strong{display:block;font-size:16px;color:#fff}
#vpo-offre .vpo-rep-val{display:block;font-weight:600;color:var(--vpo-orange);margin:1px 0 2px}
#vpo-offre .vpo-lisere{height:6px;margin:34px calc(var(--vpo-pad)*-1) 0;background:linear-gradient(90deg,var(--vpo-rouge) 0 55%,var(--vpo-orange) 55% 82%,var(--vpo-vert) 82% 100%)}
#vpo-offre a:focus-visible{outline:3px solid #fff;outline-offset:3px}
@media (prefers-reduced-motion:no-preference){#vpo-offre .vpo-bouton,#vpo-offre .vpo-cta{transition:transform .15s ease,box-shadow .15s ease,background-color .15s ease}}
#vpo-offre .vpo-bouton:hover,#vpo-offre .vpo-cta:hover{background:#FFBF3F;transform:translateY(-1px);box-shadow:0 8px 20px rgba(0,0,0,.22)}
@container (min-width:620px){
#vpo-offre .vpo-missions,#vpo-offre .vpo-listes,#vpo-offre .vpo-grille-2{grid-template-columns:repeat(2,minmax(0,1fr))}
#vpo-offre .vpo-grille-3,#vpo-offre .vpo-reperes{grid-template-columns:repeat(3,minmax(0,1fr))}
#vpo-offre .vpo-listes{align-items:start}
}
@container (min-width:760px){
#vpo-offre{--vpo-pad:48px}
#vpo-offre .vpo-hero{padding:52px var(--vpo-pad) 30px}
#vpo-offre .vpo-feuille{top:30px;right:-6%;width:36%;max-width:400px}
#vpo-offre .vpo-hero-in{max-width:64%}
#vpo-offre .vpo-titre{font-size:clamp(36px,4.8cqi,50px)}
#vpo-offre .vpo-vague{height:44px}
#vpo-offre .vpo-sec{grid-template-columns:170px minmax(0,1fr);gap:36px;padding:44px 0}
#vpo-offre .vpo-rail{display:block}
#vpo-offre .vpo-num{display:block;font-size:52px;margin-bottom:12px}
#vpo-offre .vpo-h3{font-size:30px}
#vpo-offre .vpo-candidater-haut{grid-template-columns:minmax(0,1fr) auto;gap:32px}
#vpo-offre .vpo-cta{padding:18px 24px}
#vpo-offre .vpo-cta-mail{font-size:18px}
}
"""


def json_ld():
    def puces(elements):
        return "<ul>" + "".join(f"<li>{x}</li>" for x in elements) + "</ul>"

    description = "".join([
        f"<p><strong>{fmt(ACCROCHE)} {fmt(PHRASE_CLE)}</strong></p>",
        f"<p>{fmt(CABINET)}</p>",
        "<p><strong>Vos missions</strong></p>",
        puces(f"<strong>{fmt(t)}</strong> {fmt(d)}" for t, d in MISSIONS),
        "<p><strong>Profil recherché</strong></p>",
        puces(fmt(f"{v} {l}".strip()) for v, l in FORMATION),
        f"<p>{fmt(A_DEFAUT)}</p>",
        "<p><strong>Compétences techniques</strong></p>",
        puces(f"<strong>{fmt(g)}</strong> {fmt(r)}" for g, r in COMPETENCES),
        "<p><strong>Qualités personnelles</strong></p>",
        puces(f"<strong>{fmt(g)}</strong>{'' if r.startswith(',') else ' '}{fmt(r)}" for g, r in QUALITES),
        "<p><strong>Ce que nous vous offrons</strong></p>",
        f"<p>{fmt(OFFRE)}</p>",
        puces(fmt(f"{v} : {l}") for v, l in OFFRE_FORTS + OFFRE_PLUS),
        "<p><strong>Comment candidater ?</strong></p>".replace(" ?", NBSP + "?"),
        f"<p>Envoyez votre CV et votre lettre de motivation à {EMAIL}. Nous étudions toutes les "
        "candidatures et nous nous engageons à répondre à chacune. Recrutement en 4&nbsp;étapes&nbsp;: "
        "un échange téléphonique, puis trois entretiens au cabinet.</p>",
    ]).replace("&nbsp;", " ")
    donnees = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": " ".join(TITRE),
        "description": description,
        "datePosted": DATE_PUBLICATION,
        "employmentType": "FULL_TIME",
        "hiringOrganization": {
            "@type": "Organization",
            "name": "Victimes & Préjudices Avocats",
            "sameAs": "https://www.victimesetprejudices.fr/",
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Grenoble",
                "addressRegion": "Auvergne-Rhône-Alpes",
                "addressCountry": "FR",
            },
        },
        "experienceRequirements": {"@type": "OccupationalExperienceRequirements", "monthsOfExperience": 60},
        "educationRequirements": {"@type": "EducationalOccupationalCredential",
                                  "credentialCategory": "professional certificate"},
        "jobBenefits": "PEE et PER avec abondement du cabinet, tickets restaurant",
        "industry": "Services juridiques",
    }
    return json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


bloc = "\n".join([
    "<!-- Offre d'emploi « Avocat(e) associé(e) salarié(e) » – Victimes & Préjudices Avocats.",
    "     À coller dans un bloc « HTML personnalisé » (WordPress), un widget HTML (Elementor) ou un module Code (Divi). -->",
    '<section id="vpo-offre" lang="fr" aria-labelledby="vpo-titre">',
    "<style>" + CSS.strip() + "</style>",
    *corps,
    f'<script type="application/ld+json">{json_ld()}</script>',
    "</section>",
]).replace('<h2 class="vpo-titre">', '<h2 class="vpo-titre" id="vpo-titre">')

assert "\n\n" not in bloc, "aucune ligne vide (WordPress ajouterait des <p>)"
with open(SORTIE, "w", encoding="utf8") as f:
    f.write(bloc + "\n")
print(f"Bloc généré : {SORTIE} ({len(bloc.encode('utf8')) / 1024:.1f} Ko)")
