# Bannière web 300 × 600 – Gazette du Palais 2026

Déclinaison web de la 4e de couverture de la Gazette du Palais : recrutement d'un avocat associé salarié
(H/F), en priorité, et podcast « Hervé Gerbi raconte ». Elle est diffusée sur :
- la page d'accueil du site de la Gazette du Palais ;
- les articles de la rubrique Avocats ;
- defrenois.fr ;
- actu-juridique.fr.

| Fichier | Format | Poids | Usage |
|---|---|---:|---|
| [`Banniere_300x600_animee.gif`](./Banniere_300x600_animee.gif) | GIF animé, 300 × 600 px | 103 Ko | Version à envoyer à la régie |
| [`Banniere_300x600_fixe.jpg`](./Banniere_300x600_fixe.jpg) | JPEG, 300 × 600 px | 83 Ko | Version fixe, si la régie demande une image de secours ou n'accepte pas le GIF |

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
- **Une adresse par site, si la régie l'accepte :** avec une adresse unique, toutes les visites sont comptées
  sous « gazette-du-palais », quel que soit le site. Pour savoir quel site amène des candidats, donnez une
  adresse par site en remplaçant la valeur de `utm_source` par `defrenois` ou `actu-juridique`.
- **Avant l'envoi :** vérifiez que la page s'ouvre bien.

## Contenu

- **L'offre d'abord :** la bannière s'ouvre et se termine sur l'offre, avec le bouton « Découvrir l’offre → ».
- **Pas de bouton pendant le podcast :** la bannière n'a qu'une adresse de clic, celle de l'offre. Un bouton
  « Écouter le podcast » ouvrirait donc l'offre d'emploi. Le podcast s'atteint par son QR code (« ← Scannez
  pour écouter »). Sur chaque image, le QR code affiché en pied correspond à la scène : celui de l'offre avec
  le bouton, celui du podcast sans.
- **Étiquette « RECRUTEMENT · GRENOBLE » :** la Gazette du Palais est lue dans toute la France ; le lieu du
  poste, repris de l'offre, évite des clics de candidats qui ne pourraient pas s'y installer. Pour le
  retirer, modifiez l'étiquette dans `scene_offre()`.
- **Argument :** « Perspective rapide d’association », repris de l'offre (« Ce poste est créé dans une
  perspective rapide d'association »).
- **Podcast :** un intermède de 2,9 s, avec son propre QR code.

## QR codes

Les deux QR codes de la 4e de couverture figurent en pied de la bannière, à gauche, avec une légende et le
logo à droite.

| QR code | Adresse codée | Où |
|---|---|---|
| Offre | `https://www.victimesetprejudices.fr/recrutements/avocat-associe-salarie/` | Scènes de l'offre, dont la dernière image et la version fixe, en rouge sur crème comme sur la 4e de couverture : « ← Scannez pour postuler » |
| Podcast | `https://www.victimesetprejudices.fr/podcast/` | Scène du podcast, en encre sur crème : « ← Scannez pour écouter » |

- **Pourquoi deux QR codes :**
  - le clic mène à l'offre ; le QR code du podcast est donc le seul accès au podcast depuis la bannière ;
  - celui de l'offre permet à un lecteur sur ordinateur de garder l'offre sur son téléphone.
- **Taille :** chaque module (petit carré) fait 3 px exactement, soit un QR code de 99 px (offre) ou 87 px
  (podcast). À 2 px, les codes n'étaient plus lus dans les prises de vue difficiles.
- **Lisibilité :**
  - modules posés au pixel près, foncés sur fond clair, avec 12 px de zone claire tout autour, sur toutes
    les images, transitions comprises ;
  - les deux codes sont lus dans des prises de vue simulées au téléphone : flou, bruit, reflet, rotation,
    distance, y compris dans les conditions les plus dures.
- **Adresses sans paramètres `utm_` :** des adresses plus courtes donnent des QR codes moins denses, donc plus
  faciles à lire. Ce sont les adresses des QR codes de la 4e de couverture : les visites venues des QR codes
  de la bannière et de la revue ne se distinguent donc pas.

## Déroulé de l'animation

| Temps | Scène |
|---|---|
| 0 – 2,8 s | **Offre**, sur pan crème : « Avocat associé salarié (H/F) », « Perspective rapide d’association », bouton et QR code de l'offre. À 1,5 s, la flèche du bouton avance brièvement. |
| 2,8 – 3,1 s | Un volet anthracite monte et recouvre le bouton ; en pied, le QR code du podcast remplace celui de l'offre. |
| 3,1 – 6,0 s | **Podcast**, sans bouton : « Hervé Gerbi *raconte* », « Histoires vraies d’un avocat de victimes » et QR code du podcast. |
| 6,0 – 6,3 s | Le volet crème revient avec le bouton et le QR code de l'offre. |
| 6,3 – 9,9 s | **Offre**, identique à la première image. À 7,3 s, la flèche avance de nouveau. |

Le cycle de 9,9 s est joué 3 fois, soit 29,7 s. La bannière s'arrête ensuite sur l'offre. La version fixe
reprend cette image.

## Normes des régies : à vérifier avant l'envoi

Le brief fixe le format, le poids et les types de fichiers, mais pas la durée ni la cadence de l'animation.
La bannière suit les règles les plus courantes :
- **Durée :** 30 s au plus, arrêt sur une image fixe ;
- **Cadence :** 20 images par seconde au plus (volets de 50 ms par image), sous le plafond de 24 de l'IAB.

Demandez la fiche technique de la régie. Deux cas imposeraient une variante, que le script produit en
modifiant quelques durées :
- **limite de 15 s** (certaines fiches inspirées de l'IAB) : un cycle joué une seule fois, ou deux cycles
  plus courts ;
- **plus de 200 ms par image** (règle de Google Ads pour les GIF) : des transitions sans volet ni
  mouvement de flèche.

## Reprise de la 4e de couverture

- **Photo :** le portrait d'Hervé Gerbi est extrait du visuel fourni et recadré serré sur le visage (le haut
  des cheveux est coupé, pour faire place au pied). Le pan reste à au moins 14 px du visage.
- **Pan coupé en diagonale :** il reprend le pan crème du bloc recrutement.
- **Titres :** DM Serif Display, la police du visuel, avec un filet sous le titre (rouge pour l'offre,
  orange pour le podcast). « raconte » est en italique orange.
- **Étiquettes :** « RECRUTEMENT · GRENOBLE » et « PODCAST » en Poppins SemiBold, avec un espacement des
  lettres et un pictogramme (groupe, casque).
- **Couleurs relevées sur le visuel :**
  - crème `#F4F0E7` ;
  - rouge `#B52026` ;
  - orange `#FCAF19` ;
  - vert `#8EC33F` ;
  - anthracite `#333333` ;
  - encre des titres `#151F24`.

  S'y ajoute un orange foncé, `#8C5800`, absent du visuel : il sert au mot « Scannez » du podcast, sur
  crème, où l'orange de la charte ne serait pas assez contrasté (contraste de 5,3:1).
- **Logo :** 125 px de large, en pied de chaque scène.
- **Liseré tricolore :** il ferme la bannière, comme sur les autres supports du cabinet.
- **Filet gris de 1 px :** il entoure la bannière, pour la détacher des pages blanches des sites.

## Régénérer et contrôler la bannière

```bash
pip install pillow numpy segno zxing-cpp
npm install @expo-google-fonts/dm-serif-display @expo-google-fonts/poppins \
            @expo-google-fonts/open-sans material-design-icons-iconfont
python3 generer_banniere.py node_modules
python3 -I verifier_banniere.py Banniere_300x600_animee.gif Banniere_300x600_fixe.jpg controle \
        https://www.victimesetprejudices.fr/recrutements/avocat-associe-salarie/ \
        https://www.victimesetprejudices.fr/podcast/
```

- **`generer_banniere.py` échoue si :**
  - un fichier dépasse 150 Ko ;
  - le GIF relu ne redonne pas exactement les images calculées ;
  - la zone claire d'un QR code est encombrée ;
  - le pan s'approche à moins de 14 px du visage.
- **`verifier_banniere.py` contrôle :**
  - les dimensions, les poids et la durée totale ;
  - la concordance entre la dernière image du GIF et le JPEG ;
  - la lecture des QR codes à l'écran et dans des prises de vue simulées.

  Il produit aussi, dans le dossier `controle`, une planche des scènes et un rapport.
- **Modifier la bannière (`generer_banniere.py`) :**
  - les textes : dans `scene_offre()`, `scene_podcast()`, `bouton()` (offre seulement) et `pied()` ;
  - les durées : dans `images_animation()`, `coup_de_pouce()`, `volet()` et `CYCLE` ;
  - la grille et les couleurs : en tête du script.
- **Fichiers en cas d'échec :** le script écrit d'abord sous un nom provisoire. Si un contrôle échoue, les
  fichiers précédents sont conservés.

**Ressources :**
- `ressources/photo_herve_gerbi.jpg` est extraite du PDF de la 4e de couverture ;
- `ressources/logo.png` est le logo déjà utilisé pour la fiche et l'offre d'emploi.
