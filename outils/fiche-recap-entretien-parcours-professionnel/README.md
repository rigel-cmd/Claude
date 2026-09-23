# Fiche d'information : quatre dispositifs pour faire évoluer son parcours professionnel

Fiche A4 recto-verso, aux couleurs de **Victimes & Préjudices Avocats**, remise au collaborateur lors de
son entretien de parcours professionnel. Elle porte exclusivement sur les quatre dispositifs dont il doit
être informé à cette occasion :

1. le conseil en évolution professionnelle (CEP) ;
2. la validation des acquis de l'expérience (VAE) ;
3. le compte personnel de formation (CPF) ;
4. la dotation du cabinet (abondement du CPF par l'employeur).

Le contenu est adapté au cabinet :
- **vocabulaire :** « le cabinet » plutôt que « l'entreprise » ou « l'employeur » ;
- **acteurs de la branche des cabinets d'avocats :** l'OPCO EP (opérateur de compétences de la branche) et l'ENADEP (école de formation du personnel des avocats) ;
- **lieux d'accueil Mon CEP à Grenoble et Annecy**, là où le cabinet est implanté ;
- **carte Apec :** elle cible les cadres du cabinet, dont les avocat(e)s salarié(e)s.

| Fichier | Usage |
|---|---|
| [`Fiche_dispositifs_evolution_professionnelle.pdf`](./Fiche_dispositifs_evolution_professionnelle.pdf) | Version prête à imprimer ou à envoyer par e-mail |
| [`Fiche_dispositifs_evolution_professionnelle.docx`](./Fiche_dispositifs_evolution_professionnelle.docx) | Version modifiable, avec les polices Poppins et Open Sans incorporées |

## Contenu

Chaque dispositif suit la même grille éditoriale à deux colonnes :

- **colonne d'appel :** la pastille pictogramme et la question-besoin ;
- **colonne principale :** surtitre numéroté, titre, phrase d'accroche, puis les faits (cartes crème clair à filet de couleur, chiffres clés).

- **Recto**
  - Bandeau d'ouverture « Faire évoluer votre parcours professionnel », avec le sommaire CEP · VAE · CPF · Dotation.
  - **01 · CEP :** contacts Apec et Mon CEP par Avenir Actifs, déroulé, autres situations.
  - **02 · VAE :** quatre chiffres clés (congé de 48 h, 6 à 8 mois, 1 référent, financement CPF) et démarche.
- **Verso**
  - **03 · CPF :** 500 € et 800 € par an, participation de 150 € depuis le 2 avril 2026, plafonds 2026, règles d'absence.
  - **04 · Dotation du cabinet :** dotation mobilisée en premier, participation de 150 € non due, formations métier de l'ENADEP.
  - Bandeau de clôture en vague, qui porte le mémo « Où vous informer ? » (placé dans le pied de page du verso pour rester calé en bas).

**Sources :** apec.fr, ara.avenir-actifs.org, vae.gouv.fr, moncompteformation.gouv.fr et son portail
employeurs, opcoep.fr, enadep.com. Informations à jour au 23 septembre 2026 : les montants du CPF sont révisés régulièrement,
vérifiez-les avant chaque réimpression.

## Charte appliquée

- **Couleurs :** palette élargie du cabinet. Crème `#FAF0C7` pour les fonds, rouge `#B52026`, orange `#FCAF19` et vert `#8EC33F` pour les accents, bleu clair `#BCDEF0`, ardoise `#304859` pour les titres, anthracite `#333333` pour le texte. Les fonds de cartes sont des teintes claires de ces couleurs. Pour l'orange et le vert, le texte utilise une nuance foncée, pour rester lisible.
- **Polices :** Poppins (SemiBold, Medium) pour les titres, Open Sans (Regular, SemiBold) pour le texte.
- **Éléments graphiques :**
  - bandeau crème à vague en ouverture (avec la feuille du logo en grand) et en clôture ;
  - une seule surface pour les cartes (crème clair `#FDF8E6`), la couleur de chaque dispositif étant réservée aux accents (pastille, surtitre, filet, chiffres, puces) ;
  - filets de séparation entre modules et liseré tricolore en pied de page.
- **Logo :** il a été reconstitué en haute définition à partir du symbole feuille et du nom du cabinet en Open Sans Bold, car l'image fournie était trop peu définie pour l'impression. Si vous disposez du fichier officiel en haute définition, remplacez `ressources/logo.png` (ou l'image directement dans Word : clic droit › Modifier l'image).

## Régénérer la fiche

Prérequis : Python 3 avec Pillow, Node.js avec le paquet `docx`, les polices Poppins et Open Sans
(fichiers TTF, par exemple via les paquets npm `@expo-google-fonts/poppins` et
`@expo-google-fonts/open-sans`) et la police d'icônes Material Icons (paquet npm
`material-design-icons-iconfont`).

```bash
# 1. Visuels (bandeaux d'ouverture et de clôture, logo, pastilles, pictogrammes) -> ressources/
python3 graphismes.py feuille.png <dossier_polices> <MaterialIcons-Regular.ttf> ressources

# 2. Word avec polices incorporées
node generer_fiche.js Fiche_dispositifs_evolution_professionnelle.docx ressources <dossier_polices>

# 3. PDF : générer une copie sans polices incorporées (polices installées sur le poste),
#    puis la convertir avec LibreOffice
node generer_fiche.js pour_pdf.docx ressources
soffice --headless --convert-to pdf pour_pdf.docx
```

La date de mise à jour figure dans la constante `DATE_MAJ` de `generer_fiche.js`.
