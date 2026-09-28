# Offre d'emploi « Avocat(e) salarié(e) » – Victimes & Préjudices Avocats

Deux versions de l'offre, chacune en Word et en PDF (A4 recto-verso) :

| Fichier | Contenu |
|---|---|
| [`Offre_emploi_avocat_modifiee.docx`](./Offre_emploi_avocat_modifiee.docx) · [`.pdf`](./Offre_emploi_avocat_modifiee.pdf) | Document d'origine, mise en page conservée, avec les modifications demandées |
| [`Offre_emploi_avocat_version_contrastee.docx`](./Offre_emploi_avocat_version_contrastee.docx) · [`.pdf`](./Offre_emploi_avocat_version_contrastee.pdf) | Version alternative : mêmes modifications, mise en page plus contrastée |

## Modifications de texte (communes aux deux versions)

- **Question de la section 02 :** « Prêt(e) à piloter vos dossiers en autonomie ? » devient « Prêt(e) à relever de nouveaux défis ? ».
- **Question de la section 04 :** « Un projet qui s'inscrit dans la durée ? » devient « Une ambition à la hauteur de la vôtre ? ».
- **Phrase clé mise en avant :** « Nous recherchons aujourd'hui un(e) avocat(e) démontrant un fort leadership et une capacité à prendre à terme le relais dans l'animation du cabinet. Ce poste est créé dans une perspective rapide d'association. »
  - version modifiée : encadré crème à filet rouge, en Poppins, dans la section 01 ;
  - version contrastée : la phrase ouvre le document, en blanc sur le bandeau ardoise, et la perspective d'association est mise en orange.
- **Coquille corrigée dans le titre :** il manquait l'espace de « Avocat(e) salarié(e) ».

## Harmonisations propres à la version contrastée

- **Mission « Piloter » :** « un portefeuille de dossiers jusqu'à l'indemnisation définitive » (la mention « en autonomie » est retirée).
- **Section 04 :** « Vous avancez vers l'association par étapes. Vous prendrez en charge des responsabilités progressivement. » remplace « Une perspective d'association jalonnée dans le temps, et un périmètre de responsabilités large, avec une vraie latitude de décision et une exposition client directe ».
- **Sous-titre :** « Un poste évolutif vers une possible association » est remplacé par la phrase clé du recrutement.

## Version contrastée : principes

- **Bandeau d'ouverture et pied du verso** sur fond ardoise `#304859`, avec le texte en blanc et les accents en orange `#FCAF19`. Le logo est placé en réserve (texte blanc).
- **Grands numéros de section** en rouge `#B52026` dans la colonne d'appel.
- **Missions :** cartes blanches bordées, avec une barre rouge.
- **Tuiles « profil » :** pleines, en ardoise.
- **Tuiles « offre » :** pleines, en rouge, complétées de tuiles crème.
- **Listes de compétences** sous un bandeau d'en-tête sombre.
- **Texte courant** plus foncé (`#262626`) pour la lisibilité.
- **Pied du verso « Comment candidater ? » :**
  - un bloc orange d'appel à candidater, avec l'adresse de candidature ;
  - trois repères pratiques (lieu, contrat, recrutement), avec des pastilles rouge, orange et vert assorties au liseré ;
  - une ligne de pied de page sous un filet.

  Le liseré tricolore termine les deux pages.

## Régénérer la version contrastée

```bash
python3 graphismes_offre.py feuille.png OpenSans_700Bold.ttf ressources
node generer_offre_contrastee.js Offre_emploi_avocat_version_contrastee.docx ressources <dossier_polices>
```

Les pictogrammes « Informations pratiques » et le liseré viennent de l'offre d'origine
(`ressources/ico_*.png`, `ressources/lisere.png`). Le PDF est produit à partir d'une copie générée
sans polices incorporées (`node generer_offre_contrastee.js pour_pdf.docx ressources`), convertie
avec LibreOffice.

## Budget de diffusion

[`Budget_diffusion_offre_avocat.xlsx`](./Budget_diffusion_offre_avocat.xlsx) estime le budget mensuel de
la recherche de candidats. Il est généré par `generer_budget.py`.

- **Onglet Budget :**
  - paramètres : début, durée de la campagne, HT ou TTC, TVA, scénario retenu ;
  - tableau des plateformes : tarif, facturation (gratuit, forfait, par jour, par semaine, par mois) et quantités mensuelles pour trois scénarios ;
  - budget du scénario retenu : mensuel moyen, décaissement du 1er mois, total de la campagne en HT et TTC ;
  - synthèse comparative des scénarios.
- **Onglet Échéancier :** dépenses du scénario retenu, mois par mois sur 12 mois au plus. Les forfaits sont payés au début de leur période et renouvelés au besoin.

**Scénarios par défaut (modifiables), pour 2 mois :**

| Scénario | Contenu | Mensuel moyen | 1er mois | Total HT |
|---|---|---:|---:|---:|
| Essentiel | Gratuits + Village de la Justice | 145 € | 290 € | 290 € |
| Équilibré | + boosts LinkedIn 15 j et Meta 10 j par mois, Indeed 2 semaines par mois | 595 € | 740 € | 1 190 € |
| Intensif | + boosts LinkedIn et Meta tous les jours, Indeed 4 semaines par mois | 1 145 € | 1 290 € | 2 290 € |
