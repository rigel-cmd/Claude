# Outil de suivi des entretiens de parcours professionnel (EPP)

Classeur Excel de pilotage des entretiens de parcours professionnel issus de la **loi n° 2025-989
du 24 octobre 2025** (JO du 25/10/2025, en vigueur depuis le **26 octobre 2025**), qui réécrit
l'article L6315-1 du Code du travail.

**Fichier :** [`Suivi_Entretiens_Parcours_Professionnel.xlsx`](./Suivi_Entretiens_Parcours_Professionnel.xlsx)
· compatible Excel 2010 et versions ultérieures, ainsi que LibreOffice. Aucune macro.

---

## Onglets

| Onglet | Rôle |
|---|---|
| **Mode d'emploi** | Mode opératoire, règles de calcul, codes couleur, points de vigilance |
| **Tableau de bord** | Indicateurs, contrôles de saisie, cas particuliers, exposition à l'abondement CPF, répartition par service, plan de charge sur 12 mois |
| **Suivi EPP** | Une ligne par salarié (500 lignes préformatées) : échéances et statuts calculés |
| **Journal** | Historique des entretiens réalisés (1 000 lignes) : la date la plus récente alimente le suivi |
| **Paramètres** | Délais légaux modifiables, effectif, listes déroulantes |

## Calcul de la prochaine échéance

| Situation | Échéance calculée |
|---|---|
| Moins d'un an d'ancienneté, aucun entretien | Date d'embauche + 12 mois |
| **Plus d'un an d'ancienneté** | **Date du précédent entretien professionnel + 4 ans** (saisie en colonne L ou reprise du Journal) |
| Précédent entretien dont le délai de 2 ans était déjà expiré au 26/10/2025 | Précédent entretien + 2 ans : retard à régulariser (règle transitoire désactivable) |
| Plus d'un an sans date de précédent entretien | En retard, avec l'alerte « Précédent entretien à renseigner » |

Cas particuliers également suivis :

- EPP de reprise après une absence, avec dispense si un EPP a eu lieu dans les 12 mois précédant la reprise ;
- EPP dans les 2 mois suivant la visite médicale de mi-carrière ;
- EPP de fin de carrière, dans les 2 ans précédant le 60e anniversaire ;
- état des lieux récapitulatif tous les 8 ans, avec le risque d'abondement correctif de 3 000 € sur le CPF dans les entreprises d'au moins 50 salariés.

## Prise en main

1. **Paramètres :** renseigner l'effectif, compléter la liste des services, puis adapter les délais si un accord collectif le prévoit.
2. **Suivi EPP :** saisir uniquement dans les colonnes jaunes. Pour tout salarié ayant plus d'un an d'ancienneté, renseigner la date du précédent entretien professionnel.
3. **Journal :** consigner chaque nouvel entretien. Le suivi se met à jour sans ressaisie.
4. Effacer le contenu des lignes d'exemple fictives `EX-001` à `EX-012` (touche Suppr) **sans supprimer les lignes**, afin de conserver les formules.

## Régénérer le classeur

```bash
python3 generer_outil.py Suivi_Entretiens_Parcours_Professionnel.xlsx
```

Le script (openpyxl) décrit l'ensemble des colonnes, formules, validations et mises en forme. Il permet de
modifier l'outil puis de le reconstruire à l'identique.

> Outil d'aide au pilotage : il ne remplace pas l'analyse juridique de situations particulières ni la
> vérification des textes en vigueur (Légifrance) et de l'accord de branche applicable.
