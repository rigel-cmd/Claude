# Bannière web 300 × 600 – Gazette du Palais 2026

Déclinaison web de la 4e de couverture de la Gazette du Palais (podcast « Hervé Gerbi raconte » et
recrutement d'un avocat associé salarié). Elle est diffusée sur :
- la page d'accueil du site de la Gazette du Palais ;
- les articles de la rubrique Avocats ;
- defrenois.fr ;
- actu-juridique.fr.

| Fichier | Format | Poids | Usage |
|---|---|---:|---|
| [`Banniere_300x600_animee.gif`](./Banniere_300x600_animee.gif) | GIF animé, 300 × 600 px | 120 Ko | Version à envoyer à la régie |
| [`Banniere_300x600_fixe.jpg`](./Banniere_300x600_fixe.jpg) | JPEG, 300 × 600 px | 55 Ko | Version fixe, si la régie demande une image de secours ou n'accepte pas le GIF |

Les deux fichiers respectent la limite de 150 Ko (150 000 octets).

## URL de redirection

```
https://www.victimesetprejudices.fr/recrutements/avocat-associe-salarie/?utm_source=gazette-du-palais&utm_medium=banniere&utm_campaign=recrutement-associe-2026
```

- **Page de destination :** l'offre « Avocat associé salarié ». C'est la page du QR code « Recrutement » de la
  4e de couverture.
- **Paramètres `utm_` :** ils permettent de compter, dans Google Analytics, les visites venues de la
  bannière. Ils ne changent rien à l'affichage de la page. Si le site n'a pas d'outil de mesure, donnez
  l'adresse sans eux : `https://www.victimesetprejudices.fr/recrutements/avocat-associe-salarie/`.
- **Avant l'envoi :** vérifiez que la page s'ouvre bien.

## Déroulé de l'animation

| Temps | Scène |
|---|---|
| 0 – 2,7 s | **Podcast**, sur pan anthracite : « Hervé Gerbi *raconte* » et « Histoires vraies d'un avocat de victimes » |
| 2,7 – 2,9 s | Un volet crème monte |
| 2,9 – 6,0 s | **Recrutement** : « Avocat associé salarié (H/F) » et « Rejoignez un cabinet exclusivement dédié à la défense des victimes » |
| 6,0 – 6,2 s | Le filet rouge s'épaissit et devient un bouton |
| 6,2 – 10 s | **Appel à l'action** : bouton « Découvrir l'offre → » |

Le cycle de 10 s est joué 3 fois, soit 30 s (la durée maximale usuelle des régies). La bannière s'arrête
ensuite sur la scène finale, qui réunit l'offre, le bouton et le logo. La version fixe reprend cette scène.

## Reprise de la 4e de couverture

- **Photo :** le portrait d'Hervé Gerbi est extrait du visuel fourni et recadré sur le visage.
- **Pan coupé en diagonale :** il reprend le pan crème du bloc recrutement.
- **Titres :** DM Serif Display, la police du visuel. « raconte » est en italique orange.
- **Étiquettes :** « PODCAST » et « RECRUTEMENT » en Poppins SemiBold, avec un espacement des lettres et un pictogramme (casque, groupe).
- **Couleurs relevées sur le visuel :**
  - crème `#F4F0E7` ;
  - rouge `#B52026` ;
  - orange `#FCAF19` ;
  - vert `#8EC33F` ;
  - anthracite `#333333` ;
  - encre des titres `#151F24`.
- **Logo :** il figure en bas de chaque scène, en version réserve sur le pan anthracite.
- **Liseré tricolore :** il ferme la bannière, comme sur les autres supports du cabinet.
- **Filet gris de 1 px :** il entoure la bannière, pour la détacher des pages blanches des sites.
- **Pas de QR code :** il ne servirait à rien à l'écran, puisque toute la bannière est cliquable.

## Régénérer la bannière

```bash
pip install pillow numpy
npm install @expo-google-fonts/dm-serif-display @expo-google-fonts/poppins \
            @expo-google-fonts/open-sans material-design-icons-iconfont
python3 generer_banniere.py node_modules
```

Le script indique le poids de chaque fichier et échoue si l'un d'eux dépasse 150 Ko. Les textes, les durées
des scènes et la grille se modifient en tête de `generer_banniere.py` et dans ses fonctions `scene_*`.

**Ressources :**
- `ressources/photo_herve_gerbi.jpg` est extraite du PDF de la 4e de couverture ;
- `ressources/logo.png` et `ressources/logo_reserve.png` sont les logos déjà utilisés pour la fiche
  et l'offre d'emploi.
