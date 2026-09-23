# Fiche récapitulative à remettre lors de l'entretien de parcours professionnel

Fiche A4 recto-verso remise au collaborateur pendant son entretien de parcours professionnel (EPP).
Elle présente les quatre dispositifs sur lesquels le salarié doit être informé à cette occasion.

| Fichier | Usage |
|---|---|
| [`Fiche_recap_entretien_parcours_professionnel.docx`](./Fiche_recap_entretien_parcours_professionnel.docx) | Version modifiable : ajoutez votre logo dans l'en-tête et vos contacts RH |
| [`Fiche_recap_entretien_parcours_professionnel.pdf`](./Fiche_recap_entretien_parcours_professionnel.pdf) | Version prête à imprimer ou à envoyer par e-mail |

## Contenu

- **Recto : se faire accompagner**
  - Introduction : objet de l'EPP (qui n'évalue pas le travail), périodicité, compte rendu écrit.
  - Tableau « Quel dispositif pour quel besoin ? ».
  - **1. Conseil en évolution professionnelle (CEP).** Contacts Apec (cadres, jeunes diplômés) et Mon CEP par Avenir Actifs (salariés du privé et indépendants en Auvergne-Rhône-Alpes), plus un renvoi vers mon-cep.org pour les autres situations.
  - **2. Validation des acquis de l'expérience (VAE)** via France VAE : conditions, démarche, accompagnement, financement, congé VAE de 48 heures.
- **Verso : financer son projet**
  - **3. Compte personnel de formation (CPF).** Montants crédités, participation obligatoire de 150 €, plafonds issus de la loi de finances 2026, règles d'absence sur le temps de travail.
  - **4. Dotation de l'employeur.** Co-construction d'un projet, exonération de la participation.
  - « Mes prochaines étapes » (cases à cocher, contact RH) et zone de notes.

**Sources :** apec.fr, ara.avenir-actifs.org, vae.gouv.fr, moncompteformation.gouv.fr et son portail
employeurs. Informations à jour au 23 septembre 2026 : les montants du CPF sont révisés régulièrement,
vérifiez-les avant chaque réimpression.

## Régénérer la fiche

```bash
npm install docx
node generer_fiche.js Fiche_recap_entretien_parcours_professionnel.docx
soffice --headless --convert-to pdf Fiche_recap_entretien_parcours_professionnel.docx
```

La date de mise à jour figure dans la constante `DATE_MAJ` du script.
