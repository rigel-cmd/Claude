# Audit — Indemnity Calculator (`securi-calcul`)

Audit du projet Lovable **Indemnity Calculator**, calculateur d'indemnisation en dommage
corporel du cabinet Victimes & Préjudices.

| | |
|---|---|
| **Projet Lovable** | `d8b84fbc-40cd-40a8-8366-d405b3cb6c21` |
| **Commit audité** | `20a7408f` (dernière édition : 3 août 2026) |
| **Date de l'audit** | 10 septembre 2026 |
| **Pile** | TanStack Start · React 19 · Supabase · Tailwind 4 |
| **Périmètre** | ~180 fichiers, 7 migrations SQL, 168 tests Vitest |

**Rapport complet :** [`audit-2026-09-10.html`](./audit-2026-09-10.html)
· [version publiée](https://claude.ai/code/artifact/1e587c72-af9a-46af-9699-5ec7ad30c6ec)

---

## Répartition des constats

| Gravité | Nombre |
|---|---:|
| Critique | 1 |
| Élevé | 4 |
| Moyen | 9 |
| Faible | 7 |
| **Total** | **21** |

## Les trois angles morts

1. **F1 — Les référentiels versionnés ne pilotent aucun chiffre.** Toute la mécanique base de
   données (référentiels → éditions → valeurs → épinglage par dossier → bandeau « Recalcul
   disponible ») fonctionne, mais `capitalisation.ts`, `esperance.ts` et `revalorisation.ts`
   importent les JSON figés du bundle. Un administrateur qui met à jour un barème, l'active et
   recalcule un dossier voit l'interface confirmer l'opération sans qu'aucun montant ne bouge.

2. **F2 / F3 — Deux zéros silencieux dans des cas réalistes.** Un taux d'AIPP fractionnaire entre
   deux tranches (5,5 % ; 10,5 %…) renvoie une valeur du point de 0 €, donc un DFP à 0 €. Sur tables
   prospectives, toute victime de 90 ans ou plus à la liquidation obtient un PER nul, donc une
   capitalisation nulle sur tous les postes futurs.

3. **S1 — Escalade vers les référentiels globaux.** Tout compte authentifié peut créer un cabinet,
   en devenir administrateur, et de ce seul fait éditer et activer les référentiels partagés par
   tous les cabinets. L'impact est aujourd'hui masqué par F1 — **corriger S1 avant F1**.

## Inventaire des constats

### Fidélité des calculs

| Code | Gravité | Constat |
|---|---|---|
| F1 | Critique | Les référentiels versionnés ne sont branchés sur aucun calcul |
| F2 | Élevé | PER nul, sans erreur, au-delà de 89 ans en tables prospectives |
| F3 | Élevé | Un taux d'AIPP fractionnaire entre deux tranches annule le DFP |
| F4 | Élevé | L'ATP temporaire n'accepte aucune créance de tiers payeur |
| F5 | Moyen | ATP permanente : facteur d'annualisation différent de la formule prescrite |
| F6 | Moyen | DSA récurrentes : décompte d'occurrences remplacé par une fraction d'année |
| F7 | Moyen | PGPA : la durée d'arrêt compte un jour de plus que DATEDIF |
| F8 | Moyen | DSA : la créance TP est revalorisée alors que la spec la reprend nominale |
| F9 | Moyen | Deux fonctions `joursEntre` concurrentes, aux conventions opposées |
| F10 | Faible | Intérêts au taux légal : année fixée à 365 jours |
| F11 | Faible | Codes d'avertissement déclarés jamais émis ; `esperanceRestante` mal nommée |

### Sécurité et cloisonnement

| Code | Gravité | Constat |
|---|---|---|
| S1 | Élevé | Tout compte authentifié peut s'octroyer l'édition des référentiels globaux |
| S2 | Moyen | La politique `dossier_editions` exclut les dossiers sans cabinet |
| S3 | Moyen | Un dossier peut être rattaché à un cabinet dont on n'est pas membre |
| S4 | Faible | `journal_audit` et `app_roles` lisibles par tout compte authentifié |
| S5 | Faible | `.env` est versionné (clés publiables uniquement — pas de fuite à ce jour) |
| S6 | Faible | Aucune validation de schéma sur le contenu d'un dossier |

### Qualité logicielle

| Code | Gravité | Constat |
|---|---|---|
| Q1 | Moyen | Aucune vérification de types en intégration continue |
| Q2 | Moyen | Requêtes N+1 sur le journal d'activité et la liste des référentiels |
| Q3 | Faible | Couverture de tests centrée sur les primitives, pas sur les montants finaux |
| Q4 | Faible | Écarts assumés au fichier Excel de référence non documentés |
| Q5 | Faible | Interface et accessibilité : rien de bloquant (vigilance sur `PeriodeDFT.taux`) |

## Plan d'action

| Lot | Objet | Quand | Effort |
|---|---|---|---|
| 1 | Zéros silencieux (F3, F2, F11, Q3) | Avant tout usage réel | ~1 j |
| 2 | Cloisonnement (S1, S3, S2, S4, S5) | Avant ouverture à d'autres cabinets | ~1 j |
| 3 | Créances de tiers payeurs (F4, §9.5–9.6) | — | ~2 j |
| 4 | Décision sur les référentiels (F1) | — | ~3–5 j, ou 1 h |
| 5 | Conventions et dette (F5–F9, Q1, Q2, Q4, S6, Q5) | — | ~2 j |

L'ordre compte : corriger F1 avant S1 reviendrait à ouvrir l'accès aux barèmes de tous les cabinets.

## Ce qui est solide

- La grille du point d'AIPP est exacte valeur par valeur, y compris l'exemple de contrôle Mornet
  (25 ans, 32 %, 3 740 €/point).
- Les six barèmes de capitalisation sont complets et contigus (lignes 0–104, colonnes 1–104), et les
  deux valeurs de contrôle du cahier des charges passent (47,919 et 51,328).
- La règle du droit de préférence de la victime est implémentée à la lettre et testée.
- Les dates suivent DATEDIF sans dérive de fuseau.
- RLS activée partout, `SECURITY DEFINER` avec `search_path` figé, écritures du journal réservées au
  `service_role`, validation Zod sur chaque fonction serveur, client admin chargé paresseusement.
- Le module d'intérêts refuse de calculer plutôt que d'inventer un taux (`TauxLegalManquantError`).
- Charte graphique correctement traduite en jetons CSS, feuille d'impression A4 soignée.

## Méthode

Lecture du code via l'API Lovable : 7 migrations SQL, couche d'authentification et fonctions
serveur, intégralité de `src/lib/calculs/`, couche référentiels, données de `src/data/` (vérifiées
par script : structure, contiguïté des index, valeurs nulles, valeurs de contrôle), design system et
outillage.

**Non couvert :** exécution de la suite de tests (le projet n'est lié à aucun dépôt GitHub), test
d'intrusion sur l'instance Supabase, revue ligne à ligne des 22 fichiers de routes et des composants
`ui/` issus de shadcn. Les constats de sécurité sont établis par lecture des politiques RLS et des
fonctions serveur, non par exploitation.
