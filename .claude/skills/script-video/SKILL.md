---
name: script-video
description: Rédige le script d'une vidéo hebdomadaire d'Hervé Gerbi (cabinet Victimes & Préjudices) à partir d'un sujet d'actualité ou d'un lien vers un article. Utiliser dès qu'on demande un script vidéo, un texte à dire face caméra, une prise de parole d'Hervé Gerbi, un post vidéo LinkedIn du cabinet, ou la déclinaison d'une actualité juridique en vidéo d'une minute. Restitue le rythme, les figures et la position d'énonciation de l'auteur.
---

# Script vidéo — Hervé Gerbi

Produit le script d'une vidéo hebdomadaire de 1 min à 1 min 20, dite face caméra par
Hervé Gerbi, avocat au cabinet Victimes & Préjudices (dommage corporel, défense des victimes).

**Entrée :** un sujet d'actualité, un lien vers un article, ou un texte collé.
**Sortie :** un script prêt à dire, découpé en groupes de souffle, avec deux chutes de rechange.

## Avant d'écrire

Lire `references/style-herve-gerbi.md` (l'anatomie du style, les figures, les interdits)
et `references/gabarits.md` (les quatre structures récurrentes). Le corpus de référence
— cinq transcriptions réelles — est dans `references/corpus/`. En cas de doute sur une
tournure, trancher en relisant le corpus, pas en improvisant.

## Procédure

### 1. Récupérer la matière

- **Lien fourni** → charger `WebFetch` via `ToolSearch` et lire l'article. Extraire : les
  faits, la date, les chiffres, les citations, la décision de justice s'il y en a une.
  Article inaccessible ou payant → demander à l'utilisateur de coller le texte, ne pas
  reconstituer de mémoire.
- **Sujet seul** → si l'actualité est récente et que les faits comptent, vérifier par
  `WebSearch`. Ne jamais inventer une date, un montant, un nom de juridiction ou un
  numéro d'article.
- Repérer ce qui relève du **droit stable** (ce qu'on peut affirmer) et ce qui relève de
  **l'affaire en cours** (ce qu'on commente sans trancher).

### 2. Fixer l'angle unique

Une vidéo = une idée. L'écrire d'abord en une phrase pour soi :
« Ce que je veux qu'on retienne, c'est ___. »
Si deux idées se disputent la place, en garder une et proposer l'autre comme sujet de la
semaine suivante. Un script à deux idées est un script raté.

### 3. Choisir le gabarit

A — décryptage d'actualité judiciaire · B — controverse / combat de prévention ·
C — conseil pratique saisonnier · D — pédagogie du métier.
Détail et enchaînements dans `references/gabarits.md`.

### 4. Écrire la chute en premier

C'est elle qui commande tout le reste. Tant qu'elle n'est pas trouvée, ne pas écrire le
corps. Quatre formes au choix : antithèse, comparatif « c'est bien / c'est mieux »,
appel à l'action sec, trait d'humour qui retombe sur le métier.

### 5. Écrire l'accroche, puis le corps

L'accroche nomme le sujet en 3 à 12 mots et la position est prise dans la foulée. Le corps
décline **un seul** argument sous deux ou trois angles, avec **au moins une anaphore**.

### 6. Calibrer et découper

130 à 200 mots (médiane du corpus : 192). Sujet grave ou émotionnel → 130-170, phrases
plus courtes. Sujet pédagogique ou pratique → 180-210, avec énumérations.
Puis découper en lignes de 2 à 6 mots, une ligne par groupe de souffle, comme dans le corpus.

### 7. Relire à voix haute et passer la checklist

## Format de sortie

Voir `references/exemple-sortie.md` pour un exemple complet.

```
**Titre de travail :** …
**Angle :** …
**Gabarit :** … (A/B/C/D)
**Calibrage :** … mots · ~1 min xx

---

<le script, une ligne par groupe de souffle>

---

**Deux autres chutes possibles**
1. …
2. …
```

Ajouter, sous le script, une ligne **« À vérifier avant tournage »** dès qu'un chiffre, une
date, une décision ou un texte de loi est cité — en nommant précisément quoi.

## Checklist

- [ ] Une seule idée, tenue du début à la fin
- [ ] Aucune formule d'ouverture : ni « bonjour », ni « aujourd'hui je vais vous parler de »
- [ ] Position prise dès les premières secondes
- [ ] Au moins une anaphore
- [ ] Une chute travaillée, pas un simple résumé
- [ ] 130 à 200 mots, aucune phrase au-delà de 25 mots
- [ ] Aucun connecteur écrit (« en outre », « par ailleurs », « force est de constater »,
      « il convient de ») — voir la liste noire dans le guide de style
- [ ] Le spectateur sait à la fin ce qu'il doit faire, exiger ou refuser
- [ ] Affaire en cours : c'est le récit, la stratégie ou le droit applicable qui sont visés,
      jamais la culpabilité affirmée comme acquise
- [ ] Aucun confrère, magistrat ou expert mis en cause nommément
- [ ] Aucun conseil qui vaudrait consultation sur un cas particulier
- [ ] Lu à voix haute : ça se dit, les respirations tombent juste
