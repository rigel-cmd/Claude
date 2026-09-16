# Gestion des candidatures — Cabinet Victimes & Préjudices

Outil de suivi des candidatures (recrutement) sous Excel, avec automatisations
**Outlook** (e-mails, rendez-vous, tâches, import de la boîte de réception) et
**Word** (fiche candidat, convocation, lettre de refus, promesse d'embauche).

## Contenu livré

| Fichier | Rôle |
|---|---|
| `Gestion_Candidatures_VP.xlsx` | Le classeur : 8 onglets, tableau de bord, listes déroulantes, alertes |
| `VP_Candidatures.bas` | Module VBA à importer pour activer les 18 boutons |
| `VP_Candidatures_a_coller.txt` | Le même code sans la ligne `Attribute`, pour un copier-coller |
| `modeles-word/*.docx` | Les 4 modèles Word à déposer dans le dossier des modèles |

## Installation (5 minutes, une seule fois par poste)

1. Ouvrir le classeur, onglet **Paramètres** : compléter les cellules crème
   (coordonnées, signataire, ville, chemins des trois dossiers de travail).
2. **Fichier ▸ Enregistrer sous ▸ Classeur Excel prenant en charge les macros (.xlsm)**.
3. Fermer Excel, puis dans l'Explorateur : clic droit sur le fichier ▸ Propriétés ▸
   cocher **Débloquer** (Windows bloque les macros des fichiers téléchargés).
4. Rouvrir, `Alt + F11` ▸ **Fichier ▸ Importer un fichier** (`Ctrl + M`) ▸ `VP_Candidatures.bas`.
   En cas d'échec : **Insertion ▸ Module**, puis coller le contenu de
   `VP_Candidatures_a_coller.txt`.
5. **Exécution ▸ Exécuter Sub/UserForm** ▸ `Installer`. Les boutons apparaissent.
6. Copier le dossier `modeles-word` à l'emplacement indiqué dans Paramètres.

Le détail figure dans l'onglet **Notice** du classeur.

## Architecture du classeur

| Onglet | Contenu |
|---|---|
| Accueil | Compteurs, 18 boutons d'automatisation, navigation, premiers pas |
| Candidatures | Le tableau de suivi : 31 colonnes, 1 ligne par candidature |
| Entretiens | Planning et comptes rendus, liés aux candidatures par l'ID |
| Tableau de bord | Statuts, postes, sources, responsables, délais, flux sur 12 mois |
| Journal | Trace horodatée des e-mails envoyés et des documents générés |
| Modèles e-mails | 7 modèles à balises `{{...}}`, librement modifiables |
| Paramètres | Identité du cabinet, dossiers, délais, 15 listes déroulantes |
| Notice | Mode d'emploi, installation, circuit type, RGPD, dépannage |

Les colonnes `Alerte`, `Délai réponse`, `Ancienneté` et `Purge RGPD le` sont
calculées. Elles s'appuient sur une cellule `Aujourdhui` unique (onglet
Paramètres) plutôt que sur un `AUJOURDHUI()` par ligne : le recalcul reste
rapide même avec plusieurs milliers de lignes.

## Régénérer les fichiers

```bash
pip install openpyxl && npm install docx
python3 build_classeur.py Gestion_Candidatures_VP.xlsx
node build_modeles_word.js modeles-word
python3 build_module.py     # produit le .bas et le .txt depuis la source UTF-8
python3 verifier.py        # contrôles de cohérence
```

`VP_Candidatures.bas` doit impérativement être en **Windows-1252** et en fins
de ligne **CRLF** : en UTF-8 les accents deviennent illisibles, et avec des fins
de ligne Unix (LF seuls) l'éditeur VBA lit le module comme une ligne unique et
l'import échoue. `build_module.py` produit et vérifie ces deux propriétés ; la
source de travail éditable est `VP_Candidatures.utf8.bas`.

## Contrôles automatisés (`verifier.py`)

- noms de feuilles, en-têtes de colonnes et plages nommées référencés par le VBA
  existent réellement dans le classeur ;
- chaque bouton pointe vers une macro publique existante ;
- structure du module (procédures et guillemets équilibrés) ;
- **format du module** : CRLF, Windows-1252, ligne `Attribute` présente ou absente
  selon le fichier, longueur de ligne et nombre de continuations dans les limites VBA ;
- toutes les balises `{{...}}` des modèles e-mail et Word sont couvertes par le VBA ;
- les 4 `.docx` sont des archives Office valides ;
- **toutes les formules du classeur s'évaluent sans erreur** (bibliothèque `formulas`).

## Conformité

Durée de conservation par défaut : **2 ans à compter du dernier contact**
(recommandation CNIL en matière de recrutement), paramétrable. La colonne
`Purge RGPD le` se recalcule seule et le bouton *Purge RGPD* anonymise les
lignes échues. Les modèles d'e-mails comportent la mention d'information et le
rappel des droits du candidat.
