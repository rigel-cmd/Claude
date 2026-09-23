# Fiche récapitulative à remettre lors de l'entretien de parcours professionnel

Fiche A4 recto-verso remise au collaborateur pendant son entretien de parcours professionnel (EPP),
aux couleurs de **Victimes & Préjudices Avocats**. Elle présente les quatre dispositifs sur lesquels le
salarié doit être informé à cette occasion.

| Fichier | Usage |
|---|---|
| [`Fiche_recap_entretien_parcours_professionnel.pdf`](./Fiche_recap_entretien_parcours_professionnel.pdf) | Version prête à imprimer ou à envoyer par e-mail |
| [`Fiche_recap_entretien_parcours_professionnel.docx`](./Fiche_recap_entretien_parcours_professionnel.docx) | Version modifiable, avec les polices Poppins et Open Sans incorporées |

## Charte appliquée

- **Couleurs :** palette élargie du cabinet. Crème `#FAF0C7` pour les fonds, rouge `#B52026`, orange `#FCAF19` et vert `#8EC33F` pour les accents, bleu clair `#BCDEF0`, ardoise `#304859` pour les titres, anthracite `#333333` pour le texte. Les fonds de cartes sont des teintes claires de ces couleurs. Pour l'orange et le vert, le texte utilise une nuance foncée, pour rester lisible.
- **Polices :** Poppins (SemiBold, Medium) pour les titres, Open Sans (Regular, SemiBold) pour le texte.
- **Éléments graphiques :**
  - bandeau crème à vague, avec la feuille du logo en grand ;
  - pastilles pictogrammes par dispositif, cartes et chiffres clés ;
  - frise du rythme des entretiens et liseré tricolore en pied de page.
- **Logo :** il a été reconstitué en haute définition à partir du symbole feuille et du nom du cabinet en Open Sans Bold, car l'image fournie était trop peu définie pour l'impression. Si vous disposez du fichier officiel en haute définition, remplacez `ressources/logo.png` (ou l'image directement dans Word : clic droit › Modifier l'image).

## Contenu

- **Recto : se faire accompagner**
  - Introduction et « Quatre dispositifs pour vous accompagner ».
  - **01 · Conseil en évolution professionnelle (CEP).** Contacts Apec (cadres, jeunes diplômés) et Mon CEP par Avenir Actifs (Auvergne-Rhône-Alpes), plus un renvoi vers mon-cep.org pour les autres situations.
  - **02 · VAE :** chiffres clés (congé de 48 h, 6 à 8 mois, financement CPF, accompagnateur), puis démarche sur vae.gouv.fr.
- **Verso : financer et suivre**
  - **03 · CPF :** 500 € et 800 € par an, participation de 150 €, plafonds 2026, règles d'absence.
  - **04 · Dotation de l'employeur.**
  - Frise « Le rythme de vos entretiens ».
  - « Mes prochaines étapes » (cases à cocher) et « Mes notes », avec le contact RH et la date de remise.

**Sources :** apec.fr, ara.avenir-actifs.org, vae.gouv.fr, moncompteformation.gouv.fr et son portail
employeurs. Informations à jour au 23 septembre 2026 : les montants du CPF sont révisés régulièrement,
vérifiez-les avant chaque réimpression.

## Régénérer la fiche

Prérequis : Python 3 avec Pillow, Node.js avec le paquet `docx`, les polices Poppins et Open Sans
(fichiers TTF, par exemple via les paquets npm `@expo-google-fonts/poppins` et
`@expo-google-fonts/open-sans`) et la police d'icônes Material Icons (paquet npm
`material-design-icons-iconfont`).

```bash
# 1. Visuels (bandeaux, logo, pastilles, frise) -> ressources/
python3 graphismes.py feuille.png <dossier_polices> <MaterialIcons-Regular.ttf> ressources

# 2. Word avec polices incorporées
node generer_fiche.js Fiche_recap_entretien_parcours_professionnel.docx ressources <dossier_polices>

# 3. PDF : générer une copie sans polices incorporées (polices installées sur le poste),
#    puis la convertir avec LibreOffice
node generer_fiche.js pour_pdf.docx ressources
soffice --headless --convert-to pdf pour_pdf.docx
```

La date de mise à jour figure dans la constante `DATE_MAJ` de `generer_fiche.js`.
