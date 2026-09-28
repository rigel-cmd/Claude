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

## Régénérer la version contrastée

```bash
python3 graphismes_offre.py feuille.png OpenSans_700Bold.ttf ressources
node generer_offre_contrastee.js Offre_emploi_avocat_version_contrastee.docx ressources <dossier_polices>
```

Les pictogrammes « Informations pratiques » et le liseré viennent de l'offre d'origine
(`ressources/ico_*.png`, `ressources/lisere.png`). Le PDF est produit à partir d'une copie générée
sans polices incorporées (`node generer_offre_contrastee.js pour_pdf.docx ressources`), convertie
avec LibreOffice.
