# Audit complet — Insurance Clarity Hub (« Contrats & Garanties » / Athéna)

**Projet Lovable** : `8ec4a5e7-265b-4e27-9f66-1e4307be3dd7`
**Espace de travail** : Greg's Lovable (plan Pro)
**Dernière édition du projet** : 12 août 2026 · **Statut de publication** : non publié
**Date de l'audit** : 5 octobre 2026

---

## 1. Synthèse exécutive

Le projet est une application React/Vite + Supabase qui fait entrer des particuliers dans un tunnel
(questionnaire → dépôt de contrats d'assurance → consultation d'avocat rédigée puis publiée). Il est
**nettement mieux construit que la moyenne des projets de ce type** : le modèle d'autorisation est le bon
patron (rôles en table dédiée, fonction `SECURITY DEFINER`, RLS partout), le stockage est cloisonné par
utilisateur avec des URLs signées à 60 secondes, la fonction serveur ne contourne jamais la RLS, aucune
faille XSS n'est ouverte, et l'accessibilité a visiblement été travaillée. Le contenu juridique (CGV,
politique de confidentialité) est d'un niveau professionnel rare sur ce type de site.

Il reste néanmoins **quatre points qui interdisent une mise en ligne en l'état**, tous liés au fait que
l'application manipule des **données de santé** (article 9 RGPD) couvertes par le **secret professionnel
de l'avocat** :

| # | Point bloquant | Gravité |
|---|---|---|
| 1 | Les données de santé des clients sont envoyées à un modèle d'IA tiers, ce que la politique de confidentialité contredit explicitement | **Critique** |
| 2 | Les mentions légales contiennent huit mentions obligatoires non renseignées (hébergeur, assurance RCP, TVA) | **Critique** |
| 3 | Les écrans « mon dossier » n'imposent pas de filtre sur l'utilisateur : un compte administrateur y voit — et peut y écraser — le dossier d'un client | **Élevé** |
| 4 | La table `consultations` (la donnée la plus sensible) n'existe dans aucune migration : sa politique RLS n'est ni auditable ni reproductible | **Élevé** |

À quoi s'ajoutent trois engagements pris envers les clients mais **non implémentés** : les durées de
conservation annoncées, l'effacement complet des pièces, et les notifications par e-mail.

**Verdict** : socle technique sain, dette de conformité importante. Comptez une à deux semaines de
travail pour lever les points P0 et P1 ci-dessous avant publication.

---

## 2. Périmètre, méthode et limites

**Examiné** : l'intégralité du dépôt (≈160 fichiers) — configuration, routage, authentification,
questionnaire, téléversement, espace client, espace administrateur, fonction serveur, les 9 migrations
SQL, les pages légales, la configuration Tailwind/TypeScript/ESLint, les tests.

**Non vérifié — à contrôler vous-même dans l'éditeur Lovable :**

> Toutes les requêtes SQL envoyées à la base du projet pendant l'audit ont échoué en **504**, y compris
> un simple `select 1`. La base Supabase est donc injoignable depuis la passerelle Lovable, probablement
> mise en veille après presque deux mois sans édition. L'accès direct à `*.supabase.co` est par ailleurs
> bloqué par la politique réseau de l'environnement d'audit.

En conséquence, **n'ont pas pu être contrôlés sur la base réelle** :

- la politique RLS de la table `consultations` (voir § 4.2) ;
- le caractère privé du bucket `contrats` et ses limites `file_size_limit` / `allowed_mime_types` ;
- les réglages Supabase Auth (confirmation d'e-mail, protection contre les mots de passe compromis,
  durée de validité des liens de réinitialisation) ;
- le volume réel de données.

Le SQL à exécuter pour lever ces points figure en **annexe A**.

---

## 3. Architecture et pile technique

| Couche | Choix | Appréciation |
|---|---|---|
| Front | React 18, Vite 5, TypeScript 5.8, React Router 6 | Standard, à jour |
| UI | Tailwind 3.4 + shadcn/ui (Radix) | Cohérent, design tokens centralisés dans `src/index.css` |
| Données | Supabase (PostgreSQL + Auth + Storage) | Adapté |
| Serveur | 1 fonction edge Deno (`generer-rappel-situation`) | Bien écrite |
| IA | Passerelle Lovable → `openai/gpt-5.6-sol` | **Problème de conformité, voir § 5.1** |
| Tests | Vitest + Playwright installés | **Aucun test réel** |

**Modèle de données** (7 tables) : `profiles`, `dossiers`, `documents`, `user_roles`, `consultations`,
`fiches_conseils`, `consultation_fiches`. Le modèle est juste : les réponses du questionnaire sont
stockées en JSONB (`dossiers.reponses`), les fiches conseils sont **recopiées** dans
`consultation_fiches` à l'insertion — modifier une fiche mère n'altère donc jamais une consultation déjà
remise. C'est exactement ce qu'il faut pour un document qui engage la responsabilité du cabinet.

**Routage** : 13 routes publiques/client + 4 routes admin protégées par `<AdminRoute>`, plus 4
redirections d'anciennes adresses. Propre.

---

## 4. Sécurité et contrôle d'accès

### 4.1 Ce qui est bien fait — à conserver tel quel

- **Le rôle administrateur est dans une table dédiée** `user_roles`, pas dans `profiles`. La fonction
  `has_role()` est `SECURITY DEFINER` avec `SET search_path = public`, et son `EXECUTE` est révoqué pour
  `anon` et `PUBLIC`. Surtout : **aucune policy INSERT/UPDATE/DELETE n'existe sur `user_roles`** et seul
  le `SELECT` est accordé à `authenticated` — l'escalade de privilèges depuis le navigateur est donc
  structurellement impossible. C'est le patron correct, rarement respecté.
- **Le stockage est cloisonné par utilisateur** : `(storage.foldername(name))[1] = auth.uid()::text`.
  Les fichiers ne sont jamais servis par URL publique, uniquement par URL signée valable **60 secondes**
  (`TableauDeBord.tsx`, `AdminDossierDetail.tsx`).
- **La fonction edge ne contourne pas la RLS** : elle crée son client Supabase avec la clé *anon* et le
  jeton de l'appelant, vérifie `auth.getUser()` puis re-vérifie `has_role(..., 'admin')` côté serveur.
  Elle n'utilise jamais la clé `service_role`. C'est la bonne façon de faire.
- **Pas de surface XSS** : aucun `dangerouslySetInnerHTML` dans le projet. `react-markdown` est utilisé
  sans `rehype-raw` (le HTML brut est donc ignoré) et le rendu des liens est explicitement neutralisé en
  `<span>` dans `FicheContenu.tsx`.
- **Pas d'open redirect** : `cheminSur()` dans `EspaceClient.tsx` valide le paramètre `?suite=` contre
  `/^\/[A-Za-z0-9\-\/]*$/` avant toute navigation.
- **Messages d'authentification non énumérants** (« l'adresse ou le mot de passe est incorrect », « si un
  espace est associé à cette adresse… »), mot de passe à 10 caractères minimum.
- Les fonctions `admin_supprimer_dossier` / `admin_supprimer_client` **re-vérifient le rôle en base**
  (`RAISE EXCEPTION` sinon) : elles ne font pas confiance à l'interface.

### 4.2 `consultations` — la table la plus sensible n'est pas auditable — **Élevé**

Le dossier `supabase/migrations/` contient 9 fichiers, mais la table `consultations` n'y est créée nulle
part : seul un `COMMENT ON TABLE public.consultations` (migration du 5 août) la mentionne. Même constat
pour la fonction `admin_supprimer_client` et pour la création du bucket `contrats`. Ces objets ont été
créés directement en base. Le code en a d'ailleurs conscience :

```ts
// src/content/consultation.ts
/**
 * La table consultations a été créée directement en base : les types générés
 * par Lovable ne la connaissent pas encore, d'où ce point d'accès non typé.
 */
const db = supabase as unknown as { from: (table: string) => any };
```

**Conséquences** : l'environnement n'est pas reproductible, la politique RLS qui protège le document
contenant l'analyse juridique complète du client ne peut être ni relue ni revue, et un éventuel écart
(policy trop permissive, RLS désactivée) passerait inaperçu.

**Correctif** : exécuter l'annexe A, puis écrire une migration de rattrapage
(`CREATE TABLE IF NOT EXISTS` + policies, idempotente) reflétant l'état réel, pour `consultations`,
`admin_supprimer_client` et le bucket `contrats`.

### 4.3 Consultation en brouillon potentiellement visible du client — **Élevé (à confirmer)**

`chargerConsultation()` (`src/content/consultation.ts`) ne filtre **pas** sur `statut = 'publiee'` :

```ts
const { data } = await tableConsultations()
  .select("id, dossier_id, contenu, statut, publiee_le, updated_at")
  .eq("dossier_id", dossierId)
  .maybeSingle();
```

Et `TableauDeBord.tsx` affiche l'encart « Votre consultation d'avocat est disponible » dès qu'une ligne
existe (`setConsultationDisponible(Boolean(consultation))`), sans regarder le statut.

La seule barrière est donc la policy RLS de `consultations` — précisément celle qu'on ne peut pas lire
(§ 4.2). À noter : la policy de `consultation_fiches`, elle, exige bien `c.statut = 'publiee'`, ce qui
laisse penser que celle de `consultations` fait de même. **Si ce n'est pas le cas, un client lit le
brouillon de son avocat.**

**Correctif (défense en profondeur, à faire dans tous les cas)** : ajouter un paramètre à
`chargerConsultation(dossierId, { publieeUniquement: true })` et l'utiliser côté client
(`ConsultationClient.tsx`, `TableauDeBord.tsx`), l'admin conservant l'accès au brouillon. Ne jamais faire
reposer une règle métier visible par l'utilisateur sur la seule RLS.

### 4.4 Requêtes « mon dossier » sans filtre utilisateur — **Élevé**

Deux requêtes s'appuient entièrement sur la RLS pour savoir « de qui » est le dossier :

```ts
// src/pages/TableauDeBord.tsx
const { data: dossiers } = await supabase.from("dossiers")
  .select("id, statut, etape_courante, reponses, envoye_le")
  .order("created_at", { ascending: false }).limit(1);   // ← aucun .eq("user_id", …)

// src/pages/Parcours.tsx
const { data: existant } = await supabase.from("dossiers")
  .select("id, reponses").eq("statut", "brouillon")
  .order("created_at", { ascending: false }).limit(1).maybeSingle();  // ← idem
```

Pour un client, la RLS (`dossiers_own_select`) limite bien au propriétaire. **Mais le compte
administrateur dispose de `dossiers_admin_select` (lecture de tous les dossiers) et de
`dossiers_admin_update` (écriture sur tous).** Donc, si Me Gerbi — ou tout futur collaborateur
administrateur — ouvre `/tableau-de-bord` ou `/parcours` :

- `/tableau-de-bord` lui affiche **le dossier du dernier client inscrit** comme étant le sien (réponses,
  documents, lien vers « sa » consultation) ;
- `/parcours` est pire : il s'accroche au dernier brouillon client (`dossierId`), puis l'effet de
  synchronisation automatique déclenche au bout de 800 ms
  `update({ reponses, etape_courante }).eq("id", dossierId)` — **les réponses du client sont écrasées**
  par celles de l'administrateur si celui-ci a quoi que ce soit en `localStorage` (par exemple après un
  test du formulaire).

**Correctif** : une ligne dans chaque requête.

```ts
.eq("user_id", user.id)
```

Et, par principe, ajouter ce filtre à toute requête « mes données » plutôt que de déléguer à la RLS, qui
n'a pas la même sémantique selon le rôle de l'appelant.

### 4.5 Contrôles de fichiers uniquement côté navigateur — **Moyen**

`PhaseContrats.tsx` valide le type MIME (`TYPES_ACCEPTES`) et la taille (20 Mo) **dans le navigateur
uniquement** — donc contournable. Il faut que le bucket `contrats` porte les mêmes limites côté serveur
(`file_size_limit`, `allowed_mime_types`), ce qui n'a pas pu être vérifié (§ 2). Le nom de fichier est
en revanche correctement assaini (`nomSecurise`, normalisation NFD + liste blanche) et le chemin est
construit avec `crypto.randomUUID()` sous `userId/dossierId/` : pas de traversée de répertoire possible.

### 4.6 Typage contourné sur les chemins les plus sensibles — **Moyen**

```ts
const db = supabase as unknown as { from: (table: string) => any };   // consultation.ts, fiches.ts
const appelerAdmin = (fn: string, args) => (supabase as unknown as { rpc: … })…  // AdminDossierDetail.tsx
```

Combiné à `"strict": false`, `"noImplicitAny": false`, `"noUnusedLocals": false`
(`tsconfig.app.json`) et à `"@typescript-eslint/no-unused-vars": "off"` (`eslint.config.js`), le filet de
sécurité TypeScript est quasi inexistant **exactement là où circulent les données de santé et le contenu
des consultations**. Il suffit de régénérer les types Supabase (`consultations`, `fiches_conseils` et
`consultation_fiches` sont désormais présentes dans `src/integrations/supabase/types.ts`) pour supprimer
ces trois contournements : **ils ne sont plus nécessaires**, le commentaire qui les justifie est périmé.

---

## 5. Conformité RGPD et déontologie

### 5.1 Données de santé transmises à un modèle d'IA tiers, non divulgué — **Critique**

`supabase/functions/generer-rappel-situation/index.ts` construit un objet `donnees` puis le POST vers
`https://ai.gateway.lovable.dev/v1/responses` avec le modèle `openai/gpt-5.6-sol`. Cet objet contient :

```ts
situationParticuliere: {
  pensionOuRente:        reponses.pension,
  tauxOuCategorie:       reponses.pensionTaux,
  organisme:             reponses.pensionOrganisme,
  antecedentsMedicaux:   reponses.antecedents,
  natureAntecedents:     reponses.antecedentsNature,     // ← « hospitalisation, ALD… »
  anneeAntecedents:      reponses.antecedentsAnnee,
  traitementEnCours:     reponses.antecedentsTraitement,
  exclusionOuSurprime:   reponses.antecedentsExclusions,
},
identite: { age, ville, codePostal, pays, nationalite, metier, statutProfessionnel, civilite }
```

Soit des **données de santé au sens de l'article 9 du RGPD**, associées à des données d'identification
indirecte (âge + ville + code postal + métier + nationalité), envoyées à un sous-traitant tiers,
très probablement hors Union européenne.

Or la page `src/pages/Confidentialite.tsx` affirme exactement l'inverse :

> « Les prestataires techniques assurant l'hébergement du service, **situés dans l'Union européenne** […] »
> « Aucune donnée de navigation n'est collectée […] et **aucun outil de mesure d'audience tiers** n'est utilisé. »
> « Ces données ne sont communiquées à **aucun** assureur, courtier, intermédiaire ou tiers commercial. »

Aucune mention d'un traitement par intelligence artificielle, d'un sous-traitant américain, ni d'un
transfert hors UE. S'ajoute, pour un avocat, le **secret professionnel** (art. 66-5 de la loi du
31 décembre 1971), dont la portée excède celle du RGPD et que le client seul peut lever.

Le prompt système demande bien au modèle de ne pas *restituer* le téléphone, l'e-mail ni l'adresse
complète — bonne intention, mais la restriction porte sur la **sortie**, pas sur ce qui est **transmis**.

**Correctifs, par ordre de préférence :**

1. **Ne pas transmettre les champs de santé.** Le « rappel de la situation » peut être rédigé sans eux,
   ou avec des catégories neutres (« antécédents déclarés : oui/non ») ; l'avocat complète à la main le
   paragraphe médical. C'est la seule option qui lève à la fois le RGPD et le secret professionnel.
2. Si la génération complète est jugée indispensable : mettre à jour la politique de confidentialité
   (sous-traitant IA nommé, finalité, pays de traitement, garanties des art. 44 à 49, durée de rétention
   côté fournisseur), **vérifier le contrat de sous-traitance Lovable/OpenAI (art. 28)**, recueillir un
   consentement spécifique distinct à l'étape récapitulative, et consigner le traitement au registre.
3. Dans tous les cas : pseudonymiser avant envoi (pas de ville + code postal + métier + âge simultanément,
   qui suffisent à ré-identifier) et désactiver toute rétention/entraînement côté fournisseur.

### 5.2 Durées de conservation annoncées, jamais appliquées — **Élevé**

La politique de confidentialité engage le cabinet sur des durées précises :

> « Dossier non finalisé et non transmis : **suppression au terme de douze mois d'inactivité**. »
> « Dossier ayant donné lieu à une consultation : conservation pendant **cinq ans** […] »
> « Pièces comptables : **dix ans** […] À l'expiration de ces durées, les données sont supprimées de
> manière irréversible. »

**Aucun mécanisme de purge n'existe dans le projet** : ni tâche planifiée, ni `pg_cron`, ni fonction edge
de nettoyage, ni colonne de date de purge. Les dossiers s'accumuleront indéfiniment. Annoncer une durée
de conservation qu'on n'applique pas est précisément ce que la CNIL relève en contrôle.

**Correctif** : une fonction edge de purge déclenchée par une tâche planifiée (`pg_cron` ou Routine
Lovable), qui supprime les dossiers `statut = 'brouillon'` dont `updated_at < now() - interval '12 months'`
(et les fichiers associés) — et journalise ses passages.

### 5.3 Effacement incomplet des pièces — **Élevé**

Dans `AdminDossierDetail.tsx`, `supprimerClient()` appelle `supprimerFichiers()`, qui ne supprime du
stockage que les fichiers **du dossier affiché** (`documents`, chargé avec `.eq("dossier_id", courant.id)`),
puis `admin_supprimer_client(p_user_id)` qui, lui, supprime **tous** les dossiers du client en cascade.

> **Si le client a plus d'un dossier, les fichiers des autres dossiers restent dans le bucket**, orphelins
> et indétectables puisque les lignes `documents` qui portaient leur chemin viennent d'être détruites.

Le même problème se pose pour toute suppression effectuée ailleurs qu'à travers cet écran (SQL direct,
cascade `ON DELETE`) : rien, côté serveur, ne nettoie le stockage. Pour une demande d'effacement RGPD
formelle, l'effacement est donc potentiellement incomplet.

**Correctif** : déplacer la suppression des fichiers côté serveur — un trigger `AFTER DELETE ON
public.documents` ou, plus simple, faire supprimer par `admin_supprimer_client` l'intégralité du préfixe
`<user_id>/` du bucket via une fonction edge dédiée. Et, dans l'écran admin, charger les chemins de
**tous** les dossiers du client avant suppression.

### 5.4 Données de santé en `localStorage`, avant tout consentement — **Moyen**

`src/pages/Parcours.tsx` persiste l'intégralité des réponses sous la clé `cg-parcours-reponses` :

```ts
useEffect(() => { localStorage.setItem(STORAGE_KEY, JSON.stringify(reponses)); }, [reponses]);
```

Cela inclut `antecedentsNature`, `antecedentsTraitement`, `pensionTaux`, `pensionOrganisme`, le nom,
la date de naissance et l'adresse — **écrits avant la création du compte et avant le recueil du
consentement santé**, qui n'intervient qu'à l'étape récapitulative. Le nettoyage n'a lieu qu'après un
envoi réussi : **un parcours abandonné laisse ces données en clair sur le poste, sans limite de durée**
(poste partagé, ordinateur familial, cybercafé).

Le stockage local est certes mentionné dans la rubrique « Cookies et traceurs » de la politique, ce qui
est à votre crédit, mais la mention ne couvre pas la sensibilité du contenu.

**Correctif** : exclure les clés `antecedents*` et `pension*` de la sauvegarde locale (les conserver en
mémoire uniquement, ou ne les persister qu'après connexion, directement en base) ; horodater l'entrée et
la purger au-delà de 24 h ; ajouter un bouton « effacer mes réponses sur cet appareil ».

### 5.5 Mentions légales incomplètes — **Critique avant publication**

`src/pages/MentionsLegales.tsx` contient huit emplacements non renseignés :

```
[NUMÉRO DE TVA INTRACOMMUNAUTAIRE]
[DÉNOMINATION SOCIALE DE L'HÉBERGEUR] · [FORME JURIDIQUE] · [ADRESSE COMPLÈTE] · [NUMÉRO DE TÉLÉPHONE]
[ASSUREUR] · [NUMÉRO DE POLICE] · [COUVERTURE GÉOGRAPHIQUE]
```

L'identification de l'hébergeur (dénomination, adresse, téléphone) est **obligatoire** au titre de
l'article 6-III de la LCEN ; les mentions relatives à l'assurance de responsabilité civile
professionnelle relèvent des obligations d'information propres à la profession d'avocat. Publier le site
avec ces crochets apparents est à la fois une non-conformité et un dommage d'image immédiat.

L'hébergeur à renseigner est, en pratique, celui de Lovable/Supabase pour l'infrastructure — à confirmer
auprès d'eux et à faire figurer tel quel.

### 5.6 Google Fonts appelé en direct — **Moyen**

`src/index.css`, première ligne :

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:…&family=Playfair+Display:…');
```

Chaque visite transmet l'adresse IP du visiteur à Google aux États-Unis, avant tout consentement. C'est
le point exact sanctionné par la jurisprudence allemande de 2022 et régulièrement relevé par la CNIL, et
il contredit frontalement vos propres affirmations (« aucun outil tiers », « prestataires situés dans
l'Union européenne »). Accessoirement, un `@import` CSS bloque le rendu : c'est aussi un gain de
performance.

**Correctif** : auto-héberger les deux familles (`@fontsource/inter`, `@fontsource/playfair-display`),
une dizaine de minutes de travail.

### 5.7 Points conformes, à souligner

- Consentement santé **distinct** du consentement général, conditionné à la présence effective de
  données de santé (`contientDonneeSante`), et bloquant pour l'envoi (`PhaseRecap.tsx`). Très bien fait.
- Les trois consentements sont **horodatés en base** (`consentement_rgpd`, `consentement_sante`,
  `consentement_honoraires` + `envoye_le`) et affichés à l'avocat : la preuve du consentement est
  conservée.
- Bandeau cookies où « Refuser » a le même poids visuel qu'« Accepter », et aucun traceur de mesure
  d'audience déposé — conforme aux recommandations CNIL.
- CGV complètes et exactes : convention d'honoraires (loi de 1971 art. 10), droit de rétractation
  (L. 221-18 s.), médiateur de la consommation de la profession d'avocat nommément désigné, contestation
  d'honoraires devant le Bâtonnier, mention explicite de l'absence d'intermédiation en assurance.
  C'est un travail juridique soigné.

---

## 6. Défauts fonctionnels confirmés

### 6.1 Le bandeau cookies est affiché deux fois — **Moyen**

`<CookieBanner />` est monté **à la fois** dans `src/components/PageLayout.tsx` (donc sur chaque page) et
dans `src/App.tsx`, après `</Routes>`. Les deux instances se superposent exactement
(`fixed inset-x-0 bottom-0`) et chacune gère son propre état `visible`, initialisé au montage.

Conséquence : l'utilisateur clique sur « Accepter », la bannière du dessus disparaît… et **la seconde
reste affichée**, l'obligeant à cliquer une deuxième fois. Deux régions ARIA identiques sont par ailleurs
exposées aux lecteurs d'écran.

**Correctif** : supprimer la ligne `<CookieBanner />` de `App.tsx` (`PageLayout` le fournit déjà partout).

### 6.2 L'indicateur d'avancement du client est faux — **Moyen**

`TableauDeBord.tsx` traduit `etape_courante` ainsi :

```ts
const PHASE_INDEX = { situation: 0, question: 0, contrats: 1, recap: 1, analyse: 2, audit: 3 };
```

Or `Parcours.tsx` écrit en base des valeurs différentes : `identite`, `statut`, `contrats`,
`mode-de-vie`, `antecedents`, `recap`, `envoye`. Quatre d'entre elles (`identite`, `statut`,
`mode-de-vie`, `antecedents`) sont absentes de la table de correspondance et retombent sur `0`.

Un client arrivé à l'étape des antécédents médicaux voit donc « Étape en cours : **Votre situation** ».
La valeur par défaut en base (`etape_courante DEFAULT 'situation'`, migration du 3 août) n'est elle-même
jamais écrite par le code actuel.

**Correctif** : une seule source de vérité pour les identifiants d'étape, partagée entre `Parcours`,
`TableauDeBord` et `src/content/libelles.ts` (`ETAPES_DOSSIER`, qui mélange aujourd'hui les deux
générations de noms).

### 6.3 La colonne « Téléphone » de l'admin est toujours vide — **Moyen**

`AdminDossiers.tsx` et `AdminDossierDetail.tsx` affichent `profiles.telephone`. Or **rien, dans tout le
projet, n'écrit jamais dans `profiles.telephone`** : à l'inscription, `EspaceClient.tsx` ne transmet que
`prenom` et `nom` en métadonnées (que le trigger `handle_new_user` recopie), et le téléphone saisi au
questionnaire reste enfermé dans le JSONB `dossiers.reponses`.

Résultat : la colonne affiche systématiquement « — » et l'avocat doit ouvrir le détail du dossier pour
trouver le numéro. Même remarque pour l'adresse postale.

**Correctif** : à l'envoi du dossier (`Parcours.envoyer`), faire un `update` de `profiles` avec
`telephone` (et éventuellement nom/prénom si l'utilisateur les a corrigés au questionnaire) — ou, plus
simplement, lire `reponses.telephone` dans l'écran admin.

À noter au passage : **l'identité est collectée deux fois** (à l'inscription *et* au questionnaire) sans
réconciliation. L'en-tête de la consultation (`ConsultationDocument.tsx`) utilise `profiles`, donc le nom
de l'inscription ; si le client a saisi une orthographe différente au questionnaire, le document officiel
portera l'autre. À arbitrer.

### 6.4 « Votre question » n'est jamais préremplie — **Faible**

`AdminConsultation.tsx` initialise le champ depuis `reponses.priorite`, qui **n'existe plus** dans
`src/content/questions.ts` (le questionnaire a été refondu le 11 août). L'interface annonce pourtant
« Question posée par le client (préremplie depuis le questionnaire) ». Soit rebrancher sur un champ
existant, soit supprimer la promesse.

### 6.5 Aucune notification n'est envoyée — **Moyen**

Plusieurs écrans promettent une information par e-mail :

- `TableauDeBord` : « Vous recevrez ensuite le montant exact des honoraires et la convention à signer » ;
- « Votre consultation d'avocat vous a été transmise » ; « vous en serez informé ».

**Aucune intégration d'envoi d'e-mail n'existe dans le projet** (pas de Resend, pas de SMTP, aucune
fonction edge de notification). Concrètement :

- le cabinet **n'est pas alerté** quand un dossier est envoyé — il faut penser à ouvrir `/admin` ;
- le client **n'est pas prévenu** quand sa consultation est publiée — il faut penser à revenir sur le site.

C'est le principal angle mort opérationnel du produit. **Correctif** : fonction edge déclenchée à
l'envoi du dossier (vers le cabinet) et à la publication de la consultation (vers le client), via Resend
— une demi-journée de travail, intégration disponible dans Lovable.

### 6.6 Robustesse du téléversement — **Moyen**

Dans `PhaseContrats.televerser()`, la séquence de remplacement d'une pièce est :

1. téléverser le nouveau fichier ;
2. supprimer l'ancien fichier du stockage ;
3. supprimer l'ancienne ligne `documents` ;
4. insérer la nouvelle ligne.

Si l'étape 4 échoue — par exemple sur violation de l'index unique `documents_unicite_piece
(dossier_id, type_contrat, groupe, piece)` en cas de double clic — **l'ancienne pièce a déjà été
détruite** et le nouveau fichier reste orphelin dans le stockage. L'utilisateur voit « Le fichier n'a pas
pu être enregistré » et a perdu la pièce précédente.

Symétriquement, `supprimer()` efface le fichier **avant** la ligne : si la suppression en base échoue, il
reste une ligne pointant vers un fichier absent, et le téléchargement échouera silencieusement.

**Correctif** : insérer d'abord (ou faire un `upsert` sur la contrainte unique), puis ne supprimer
l'ancien qu'en cas de succès. Accessoirement, la barre de progression est factice (15 % puis 80 %) : soit
utiliser la progression réelle, soit afficher un simple indicateur d'activité.

---

## 7. Accessibilité

**Niveau global : bon**, nettement au-dessus de la moyenne. À conserver :

- lien d'évitement « Aller au contenu » (`PageLayout.tsx`), un seul `<main>` par page ;
- `fieldset` / `legend` sur chaque groupe de questions, `(obligatoire)` en `sr-only` ;
- `aria-invalid` + `aria-describedby` + `role="alert"` sur les erreurs de `PhaseIdentite` ;
- `aria-live="polite"` sur les confirmations d'envoi et d'enregistrement ;
- cibles tactiles systématiquement ≥ 44 px (`h-11`, `min-h-11`) ;
- `:focus-visible` global avec anneau et décalage (`index.css`) ;
- `prefers-reduced-motion` respecté à deux niveaux : règle CSS globale **et** hook dédié dans
  `HeroAlertBanner` qui court-circuite l'animation du compteur ;
- compteur animé doublé d'un texte `sr-only` lisible (« Plus de 12 millions de victimes… »).

**À corriger :**

| Point | Détail |
|---|---|
| **Ordre des titres** (Moyen) | Sur l'accueil, `HeroAlertBanner` rend un `<h2>` **avant** le `<h1>` de `HeroSection` (`Index.tsx` monte le bandeau en premier). Faire du bandeau le `h1` de la page, ou inverser. |
| Texte compressé (Faible) | `HeroAlertBanner` : `whitespace-nowrap` + `clamp(0.875rem, 4vw, 1.75rem)` sur « Face à ce risque, êtes-vous bien assuré ? » — sur très petit écran, la phrase descend à 14 px pour éviter le retour à la ligne. Préférer un retour à la ligne à une réduction de taille. |
| Contraste à vérifier (Faible) | `text-primary-foreground/55` et `/70` sur le dégradé rouge du bandeau : à mesurer, probablement sous 4,5:1. |
| Zone cliquable (Faible) | Le bouton de retrait d'un tag (`PhaseQuestions`, `ChampTags`) fait 14 px sans surface de clic élargie. |

---

## 8. SEO, performance et contenu

### 8.1 Domaine canonique figé sur une URL de préversion — **Moyen**

`src/components/Seo.tsx` : `const SITE_URL = "https://assurance-navigator-ai.lovable.app";` — repris
aussi en dur dans `index.html` (`<link rel="canonical">`, `og:url`, et le JSON-LD `LegalService`).

Ce domaine ne correspond ni au nom du produit (« Contrats & Garanties »), ni à un domaine du cabinet, et
le projet **n'est pas publié**. Toute mise en ligne sur un autre domaine produira des balises canoniques
pointant ailleurs — c'est-à-dire, du point de vue de Google, une demande explicite de ne pas indexer vos
pages. **À reprendre impérativement avant publication**, idéalement via une variable d'environnement
unique partagée entre `index.html` et `Seo.tsx`.

### 8.2 `robots.txt` trop permissif, pas de sitemap — **Faible**

`public/robots.txt` autorise tout, y compris `/admin`, `/tableau-de-bord`, `/consultation/*` et
`/espace-client`. Le `noindex` posé à l'exécution par `Seo.tsx` protège vis-à-vis de Google (qui exécute
le JavaScript), pas des autres robots. Ajouter les `Disallow` correspondants et une directive `Sitemap:`.

Il manque par ailleurs une balise `og:image` alors que `twitter:card` est réglé sur
`summary_large_image` : les partages sur les réseaux sociaux afficheront une vignette vide.

### 8.3 Un chiffre d'accroche non sourcé en page d'accueil — **Élevé (réputationnel)**

`HeroAlertBanner.tsx` anime un compteur jusqu'à **12 000 000** « victimes d'un accident corporel » par an,
en élément le plus visible du site. Le code porte ce commentaire :

```tsx
{/* Ligne de source à activer une fois la référence validée :
<p className="mt-4 text-xs text-primary-foreground/55">Source : …</p> */}
```

Autrement dit, **la source n'est pas validée**. Pour un cabinet d'avocats dont tout le positionnement
repose sur la rigueur et l'indépendance, afficher un chiffre invérifiable en une est le risque d'image le
plus asymétrique du projet : un confrère ou un journaliste qui le conteste annule l'effet recherché.

**Correctif** : sourcer précisément (ONISR pour les accidents de la route, enquête EPAC / Santé publique
France pour les accidents de la vie courante — les ordres de grandeur diffèrent beaucoup selon le
périmètre retenu), afficher la référence sous le compteur, ou retirer le chiffre.

### 8.4 Performance

- Images servies via `*.asset.json` avec `loading="lazy"` et `decoding="async"` : bien.
- Aucun découpage de bundle : tout `App.tsx` importe les 14 pages en statique. L'espace administrateur
  (y compris l'éditeur de consultation) est donc téléchargé par chaque visiteur anonyme. Un
  `React.lazy()` sur les routes `/admin/*` et sur `ConsultationClient` réduirait sensiblement le bundle
  initial — 15 minutes de travail.
- `@import` Google Fonts bloquant le rendu (§ 5.6).
- `@tailwindcss/typography` est installé mais **absent du tableau `plugins`** de `tailwind.config.ts` :
  les classes `prose` ne produisent rien. L'utilitaire `.prose-legal` de `index.css` fait d'ailleurs le
  travail à la main. Retirer la dépendance ou brancher le plugin.

---

## 9. Qualité logicielle et industrialisation

### 9.1 Il n'y a pas de tests — **Élevé**

`src/test/example.test.ts` contient en tout et pour tout :

```ts
describe("example", () => { it("should pass", () => { expect(true).toBe(true); }); });
```

Playwright est installé et configuré (`playwright.config.ts`, `playwright-fixture.ts`) mais **aucun
scénario n'existe**. Pour une application qui héberge des données de santé et produit un document
engageant la responsabilité professionnelle du cabinet, c'est le manque le plus structurant.

**Minimum à écrire (une journée) :**

1. **Tests unitaires** sur la logique métier pure, qui est déjà bien isolée et donc facile à tester :
   `contratsADeposer()`, `validerIdentite()`, `etapeAntecedents()`, `contientDonneeSante()`,
   `calculerAge()`, `construireInventaire()` (fonction edge).
2. **Un test d'intégration du cloisonnement** : deux comptes clients, vérifier que le second ne lit ni le
   dossier, ni les documents, ni la consultation du premier. C'est le test qui compte le plus — il
   documente et verrouille la promesse centrale du service.
3. **Un parcours Playwright** de bout en bout : questionnaire → inscription → dépôt → envoi.

### 9.2 Architecture de données côté client — **Moyen**

`@tanstack/react-query` est installé et le `QueryClientProvider` est en place, mais **aucune requête ne
l'utilise** : toutes les pages rechargent à la main avec `useEffect` + `useState` + une fonction
`charger()` rappelée après chaque mutation (`AdminFiches` en appelle quatre fois). Adopter React Query
supprimerait ces rechargements manuels, apporterait cache, états de chargement et invalidation ciblée ;
sinon, autant retirer la dépendance.

Il manque par ailleurs **tout `ErrorBoundary`** : une exception de rendu dans l'espace client ou admin
produit une page blanche sans message.

### 9.3 Divers

| Point | Fichier | Gravité |
|---|---|---|
| `.env` **versionné** (pas dans `.gitignore`). Les clés présentes sont publiables (`sb_publishable_`), donc pas de fuite aujourd'hui — mais la prochaine clé secrète partira dans l'historique Git. | `.gitignore`, `.env` | Faible |
| Import inutilisé `estIndependant` — non détecté, la règle `no-unused-vars` étant désactivée. | `src/pages/Parcours.tsx` | Faible |
| `publiee_le` est réécrit à chaque republication : la date de première publication est perdue. | `AdminConsultation.tsx` | Faible |
| Aucune pagination : `AdminDossiers` charge tous les dossiers **et** tous les profils ; `AdminFiches` toute la bibliothèque. Confortable aujourd'hui, à revoir vers quelques centaines de lignes. | admin | Faible |
| Aucune journalisation des accès aux dossiers clients. Pour un cabinet, une trace « qui a ouvert quel dossier et quand » est un confort réel en cas de contestation. | — | Suggestion |

---

## 10. Plan d'action priorisé

### P0 — avant toute mise en ligne

| # | Action | Fichiers | Effort |
|---|---|---|---|
| 1 | Réveiller la base et **exécuter l'annexe A** ; corriger ce qu'elle révèle sur `consultations` et le bucket `contrats` | Supabase | 30 min |
| 2 | Décider du sort des données de santé envoyées à l'IA (§ 5.1) : les retirer du payload, ou mettre la politique de confidentialité en conformité + consentement dédié | `generer-rappel-situation/index.ts`, `Confidentialite.tsx` | 2 h à 1 j |
| 3 | Renseigner les 8 mentions légales manquantes | `MentionsLegales.tsx` | 1 h |
| 4 | Ajouter `.eq("user_id", user.id)` aux deux requêtes « mon dossier » | `TableauDeBord.tsx`, `Parcours.tsx` | 10 min |
| 5 | Filtrer `statut = 'publiee'` côté client pour la consultation | `content/consultation.ts` + appelants | 20 min |
| 6 | Corriger `SITE_URL` et les URL canoniques pour le domaine de publication réel | `Seo.tsx`, `index.html` | 15 min |

### P1 — dans le mois

| # | Action | Effort |
|---|---|---|
| 7 | Migration de rattrapage : `consultations`, `admin_supprimer_client`, bucket `contrats` | 2 h |
| 8 | Purge automatique des dossiers inactifs (engagement des 12 mois) | 0,5 j |
| 9 | Effacement complet du stockage à la suppression d'un client (trigger ou fonction edge) | 0,5 j |
| 10 | Notifications e-mail : dossier envoyé → cabinet ; consultation publiée → client | 0,5 j |
| 11 | Retirer les champs de santé du `localStorage` + purge à 24 h | 2 h |
| 12 | Supprimer le `<CookieBanner />` en double | 2 min |
| 13 | Renseigner `profiles.telephone` à l'envoi du dossier | 30 min |
| 14 | Limites `file_size_limit` / `allowed_mime_types` sur le bucket | 15 min |
| 15 | Sourcer ou retirer le chiffre de 12 millions | 1 h |

### P2 — dette technique

| # | Action | Effort |
|---|---|---|
| 16 | Tests : logique métier + cloisonnement entre clients + un parcours Playwright | 1 j |
| 17 | Auto-héberger les polices (sort de Google Fonts) | 20 min |
| 18 | Unifier les identifiants d'étape et corriger l'indicateur d'avancement | 1 h |
| 19 | Régénérer les types Supabase et supprimer les trois `as unknown as any` | 1 h |
| 20 | Activer `strict: true` et réactiver `no-unused-vars`, puis corriger | 0,5 j |
| 21 | Fiabiliser le remplacement de pièce (insérer avant de supprimer) | 1 h |
| 22 | `React.lazy()` sur les routes admin, `ErrorBoundary` global | 1 h |
| 23 | Corriger l'ordre des titres de l'accueil (h1/h2) | 15 min |
| 24 | `robots.txt` : `Disallow` sur les espaces privés + `sitemap.xml` + `og:image` | 1 h |
| 25 | `.env` dans `.gitignore` + `.env.example` | 5 min |

---

## Annexe A — SQL de vérification à exécuter dans l'éditeur Lovable

```sql
-- A1. RLS active partout, et nombre de policies par table
select c.relname                                  as table_name,
       c.relrowsecurity                           as rls_active,
       (select count(*) from pg_policies p
         where p.schemaname = 'public' and p.tablename = c.relname) as nb_policies
from pg_class c join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public' and c.relkind = 'r'
order by c.relname;
-- Attendu : rls_active = true ET nb_policies > 0 pour les 7 tables.
-- 'consultations' avec rls_active = false ou 0 policy = FUITE DE DONNÉES, à corriger immédiatement.

-- A2. Le détail des policies de consultations (le point aveugle de l'audit)
select policyname, cmd, roles::text, qual, with_check
from pg_policies where schemaname = 'public' and tablename = 'consultations';
-- Attendu : un accès admin via has_role(), et un accès client restreint à
--   EXISTS (select 1 from dossiers d where d.id = consultations.dossier_id and d.user_id = auth.uid())
--   ET statut = 'publiee'.

-- A3. Le bucket de contrats doit être privé et borné
select id, name, public, file_size_limit, allowed_mime_types from storage.buckets;
-- Attendu : public = false, file_size_limit = 20971520,
--           allowed_mime_types = {application/pdf,image/jpeg,image/png,image/webp,image/heic}

-- A4. Aucune fonction SECURITY DEFINER sans search_path figé
select p.proname, p.prosecdef, p.proconfig
from pg_proc p join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'public' and p.prosecdef
order by p.proname;
-- Attendu : proconfig contient search_path=public pour has_role, handle_new_user,
--           admin_supprimer_dossier et admin_supprimer_client.

-- A5. Fichiers orphelins dans le stockage (§ 5.3)
select count(*) as orphelins
from storage.objects o
where o.bucket_id = 'contrats'
  and not exists (select 1 from public.documents d where d.chemin = o.name);
-- Attendu : 0. Toute valeur > 0 = pièces de clients supprimés encore présentes.

-- A6. Qui est administrateur
select u.email, r.role, r.created_at
from public.user_roles r join auth.users u on u.id = r.user_id
order by r.created_at;
-- Attendu : uniquement les avocats du cabinet.
```

**À vérifier également dans le tableau de bord Supabase** (onglet Authentication → Policies/Settings) :
confirmation d'e-mail obligatoire, « Leaked password protection » activée, durée de validité des liens
de réinitialisation.

---

## Annexe B — Ce qui est à conserver tel quel

Un audit n'a d'intérêt que s'il distingue ce qu'il faut corriger de ce qu'il faut protéger. Sur ce
projet, les choix suivants sont justes et ne doivent pas être remis en cause lors des corrections :

1. **Le rôle administrateur en table séparée** avec `has_role()` `SECURITY DEFINER` et `search_path`
   figé — pas de rôle dans `profiles`, aucune policy d'écriture sur `user_roles`.
2. **La fonction edge qui réutilise le jeton de l'appelant** plutôt que la clé `service_role`, et qui
   re-vérifie le rôle côté serveur.
3. **La recopie des fiches conseils** dans `consultation_fiches` : une consultation remise est figée.
4. **Les URLs signées à 60 secondes**, jamais d'URL publique sur les contrats.
5. **Le consentement santé distinct**, conditionnel et bloquant, avec preuve conservée en base.
6. **Le rendu Markdown sans HTML brut** et les liens neutralisés dans les fiches.
7. **La qualité rédactionnelle** des CGV, de la politique de confidentialité et des micro-textes du
   parcours : le ton « avocat » est tenu de bout en bout, les promesses sont prudentes (obligation de
   moyens, pas de promesse de résultat), l'absence d'intermédiation en assurance est affirmée partout.
   C'est l'actif le plus différenciant du projet.
