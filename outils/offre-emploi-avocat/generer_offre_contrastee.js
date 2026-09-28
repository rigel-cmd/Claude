// Offre d'emploi « Avocat(e) salarié(e) » – version alternative contrastée (Word A4 recto-verso),
// charte Victimes & Préjudices Avocats.
//
// Usage :
//   npm install docx jszip
//   node generer_offre_contrastee.js [sortie.docx] [dossier_ressources] [dossier_polices]
//
// - dossier_ressources : visuels (graphismes_offre.py + pictogrammes et liseré de l'offre d'origine) ;
// - dossier_polices (facultatif) : TTF Poppins / Open Sans à incorporer au document.

const fs = require("fs");
const path = require("path");
const {
  AlignmentType, BorderStyle, CharacterSet, Document, Footer, Header,
  HorizontalPositionRelativeFrom, ImageRun, LevelFormat, Packer, PageNumber, Paragraph,
  ShadingType, Table, TableCell, TableLayoutType, TableRow, TabStopType, TextRun,
  TextWrappingType, VerticalAlign, VerticalPositionRelativeFrom, WidthType,
} = require("docx");

const SORTIE = process.argv[2] || "Offre_emploi_avocat_version_contrastee.docx";
const RES = process.argv[3] || path.join(__dirname, "ressources");
const POLICES = process.argv[4] || null;

// ---------------------------------------------------------------------------
// Charte : fonds sombres (ardoise) et accents francs pour renforcer les contrastes
// ---------------------------------------------------------------------------
const C = {
  ardoise: "304859", rouge: "B52026", orange: "FCAF19", vert: "8EC33F", creme: "FAF0C7",
  texte: "262626", secondaire: "3F4A52", filet: "D3D9DE", blanc: "FFFFFF",
  ardoiseClair: "5B7385",
};
const TITRE = "Poppins SemiBold";
const TITRE_M = "Poppins Medium";
const TEXTE = "Open Sans";
const TEXTE_G = "Open Sans SemiBold";

const dxa = (mm) => Math.round(mm * 56.6929);
const px = (mm) => (mm / 25.4) * 96;
const emu = (mm) => Math.round(mm * 36000);

const LARGEUR = 11906 - 2 * dxa(16); // 10092 DXA (178 mm)
const GOUTTIERE = 227;

// ---------------------------------------------------------------------------
// Briques
// ---------------------------------------------------------------------------
const NBSP = " ";
const typo = (s) => s
  .replace(/'/g, "’")
  .replace(/ ([:;?!])/g, NBSP + "$1")
  .replace(/« /g, "«" + NBSP).replace(/ »/g, NBSP + "»")
  .replace(/(\d) (?=\d|jours|ans|étapes)/g, "$1" + NBSP);
const t = (text, o = {}) => new TextRun({ text: typo(text), font: TEXTE, size: 18, color: C.texte, ...o });
const g = (text, o = {}) => t(text, { font: TEXTE_G, ...o });
const titreRun = (text, size, color, o = {}) => new TextRun({ text: typo(text), font: TITRE, size, color, ...o });
const surtitre = (text, color, size = 14) =>
  new TextRun({ text: typo(text), font: TITRE_M, size, color, characterSpacing: 30 });

const auto = (sp) => (sp && sp.line && !sp.lineRule ? { ...sp, lineRule: "auto" } : sp);
const p = (children, o = {}) =>
  new Paragraph({ children: [].concat(children), ...o, spacing: auto(o.spacing || { after: 0, line: 259 }) });
const espace = (mm) => new Paragraph({ children: [], spacing: { before: 0, after: 0, line: dxa(mm), lineRule: "exact" } });

function png(nom) {
  const b = fs.readFileSync(path.join(RES, nom));
  return { l: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}
function image(nom, largeurMm) {
  const { l, h, data } = png(nom);
  return new ImageRun({ type: "png", data, transformation: { width: px(largeurMm), height: px((largeurMm * h) / l) } });
}
function imageFlottante(nom, xMm, yMm, largeurMm) {
  const { l, h, data } = png(nom);
  return new ImageRun({
    type: "png", data,
    transformation: { width: px(largeurMm), height: px((largeurMm * h) / l) },
    floating: {
      horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: emu(xMm) },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: emu(yMm) },
      behindDocument: true, allowOverlap: true, lockAnchor: true, layoutInCell: false,
      wrap: { type: TextWrappingType.NONE },
    },
  });
}

const AUCUNE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const SANS = { top: AUCUNE, bottom: AUCUNE, left: AUCUNE, right: AUCUNE };
const trait = (color, size = 4) => ({ style: BorderStyle.SINGLE, size, color });

function cellule(largeur, enfants, o = {}) {
  return new TableCell({
    width: { size: largeur, type: WidthType.DXA },
    shading: o.fond ? { fill: o.fond, type: ShadingType.CLEAR, color: "auto" } : undefined,
    borders: { ...SANS, ...(o.bordures || {}) },
    margins: o.marges || { top: 0, bottom: 0, left: 0, right: 0 },
    verticalAlign: o.vAlign || VerticalAlign.TOP,
    children: enfants.length ? enfants : [p([])],
  });
}
function grille(largeurs, lignes) {
  const rows = (Array.isArray(lignes[0]) ? lignes : [lignes])
    .map((cellules) => new TableRow({ cantSplit: true, children: cellules }));
  return new Table({
    width: { size: largeurs.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: largeurs,
    layout: TableLayoutType.FIXED,
    borders: { ...SANS, insideHorizontal: AUCUNE, insideVertical: AUCUNE },
    rows,
  });
}
function colonnes(n, largeur = LARGEUR) {
  const utile = largeur - (n - 1) * GOUTTIERE;
  const base = Math.floor(utile / n);
  const res = [];
  for (let i = 0; i < n; i++) {
    res.push(i === n - 1 ? utile - base * (n - 1) : base);
    if (i < n - 1) res.push(GOUTTIERE);
  }
  return res;
}
// Rangée de cartes : contenus[i] = { enfants, fond, bordures, marges }
function cartes(largeurs, contenus) {
  let k = 0;
  return grille(largeurs, largeurs.map((l, i) => {
    if (i % 2 === 1) return cellule(l, []);
    const c = contenus[k++];
    return cellule(l, c.enfants, { fond: c.fond, bordures: c.bordures, marges: c.marges || { top: 140, bottom: 150, left: 190, right: 170 } });
  }));
}

const puce = (enfants) =>
  new Paragraph({ children: [].concat(enfants), numbering: { reference: "puceRouge", level: 0 }, spacing: { after: 50, line: 240, lineRule: "auto" } });

// ---------------------------------------------------------------------------
// Grille des sections : colonne d'appel (grand numéro + question) et colonne principale
// ---------------------------------------------------------------------------
const RAIL = dxa(36);
const ENTRE = dxa(6);
const PRINCIPALE = LARGEUR - RAIL - ENTRE;

function section({ numero, appel, surtitreTexte, titre, contenu, nouvellePage = false }) {
  return [
    new Paragraph({ children: [], pageBreakBefore: nouvellePage, spacing: { after: 0, line: 40, lineRule: "exact" } }),
    grille([RAIL, ENTRE, PRINCIPALE], [
      cellule(RAIL, [
        p(titreRun(numero, 52, C.rouge), { spacing: { after: 40, line: 240 } }),
        ...appel,
      ]),
      cellule(ENTRE, []),
      cellule(PRINCIPALE, [
        p(surtitre(surtitreTexte, C.rouge, 13), { spacing: { after: 40 } }),
        p(titreRun(titre, 33, C.ardoise), { spacing: { after: 110, line: 240 } }),
        ...contenu,
      ]),
    ]),
  ];
}
const question = (texte) => [p(titreRun(texte, 21, C.ardoise), { spacing: { after: 0, line: 250 }, indent: { right: dxa(2) } })];
const separateur = () => p([], {
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.filet, space: 1 } },
  spacing: { before: dxa(4), after: dxa(5) },
});
const paragraphe = (morceaux, after = 0) => p(morceaux.map((m) => (typeof m === "string" ? t(m) : m)), {
  alignment: AlignmentType.JUSTIFIED, spacing: { after, line: 276 },
});

// Carte de mission : fond blanc, filet fin, barre rouge à gauche
const mission = (titre, texte) => ({
  bordures: { top: trait(C.filet), right: trait(C.filet), bottom: trait(C.filet), left: trait(C.rouge, 24) },
  marges: { top: 90, bottom: 100, left: 200, right: 160 },
  enfants: [
    p(titreRun(titre, 21, C.ardoise), { spacing: { after: 20, line: 240 } }),
    p(t(texte, { size: 15, color: C.secondaire }), { spacing: { after: 0, line: 245 } }),
  ],
});

// Tuile pleine (valeur + libellé)
const tuile = (valeur, libelle, fond, couleurValeur, couleurTexte, tailleValeur = 22) => ({
  fond,
  marges: { top: 120, bottom: 130, left: 180, right: 160 },
  enfants: [
    p(titreRun(valeur, tailleValeur, couleurValeur), { spacing: { after: 30, line: 240 } }),
    p(t(libelle, { size: 15, color: couleurTexte }), { spacing: { after: 0, line: 245 } }),
  ],
});

// Carte liste avec bandeau d'en-tête sombre
function carteListe(largeur, entete, items) {
  const interieur = largeur;
  return new Table({
    width: { size: interieur, type: WidthType.DXA },
    columnWidths: [interieur],
    layout: TableLayoutType.FIXED,
    borders: { ...SANS, insideHorizontal: AUCUNE, insideVertical: AUCUNE },
    rows: [
      new TableRow({ cantSplit: true, children: [cellule(interieur, [p(surtitre(entete, C.blanc, 13))], {
        fond: C.ardoise, marges: { top: 90, bottom: 80, left: 190, right: 170 },
      })] }),
      new TableRow({ cantSplit: true, children: [cellule(interieur, items.map(([gras, reste]) => puce([g(gras, { size: 15 }), t(reste, { size: 15 })])), {
        bordures: { left: trait(C.filet), right: trait(C.filet), bottom: trait(C.filet) },
        marges: { top: 110, bottom: 60, left: 170, right: 160 },
      })] }),
    ],
  });
}

// ---------------------------------------------------------------------------
// En-têtes et pieds de page
// ---------------------------------------------------------------------------
const enTetePremiere = new Header({ children: [p(imageFlottante("bandeau_ouverture.png", 0, 0, 210))] });
const enTeteSuite = new Header({
  children: [p([
    imageFlottante("bandeau_suite.png", 0, 0, 210),
    surtitre("AVOCAT(E) SALARIÉ(E)  ·  OFFRE D'EMPLOI", C.blanc, 13),
  ], { spacing: { after: dxa(8) } })],
});

// numero : texte fixe (ex. « 2 / 2 ») ; LibreOffice ignore la couleur des champs de pagination
// sur fond sombre. À défaut, champ PAGE / NUMPAGES.
const lignePied = (couleur, numero = null) => p([
  imageFlottante("lisere.png", 0, 297 - 2.2, 210),
  t("Offre d'emploi · Victimes & Préjudices Avocats · recrutement@victimesetprejudices.fr", { size: 13, color: couleur }),
  numero
    ? new TextRun({ text: "\t" + numero, font: TITRE_M, size: 13, color: couleur })
    : new TextRun({ children: ["\t", PageNumber.CURRENT, " / ", PageNumber.TOTAL_PAGES], font: TITRE_M, size: 13, color: couleur }),
], { tabStops: [{ type: TabStopType.RIGHT, position: LARGEUR }] });

const piedPremiere = new Footer({ children: [lignePied(C.secondaire)] });

const H_CLOTURE = 70;
const COL_INFO = Array(4).fill(LARGEUR / 4);
const info = (i, icone, libelle, valeur, details) => cellule(COL_INFO[i], [
  p(image(icone, 8.5), { spacing: { after: 70 } }),
  p(titreRun(libelle, 17, C.blanc), { spacing: { after: 20, line: 235 } }),
  p(g(valeur, { size: 15, color: C.orange }), { spacing: { after: 20, line: 235 } }),
  ...[].concat(details).map((d) => p(t(d, { size: 14, color: C.creme }), { spacing: { after: 0, line: 235 } })),
], {
  marges: { top: 0, bottom: 0, left: i === 0 ? 0 : 170, right: 110 },
  bordures: i === 0 ? {} : { left: trait(C.ardoiseClair) },
});

const piedSuite = new Footer({
  children: [
    p([imageFlottante("bandeau_cloture.png", 0, 297 - H_CLOTURE, 210), surtitre("INFORMATIONS PRATIQUES", C.orange, 13)], { spacing: { after: 10 } }),
    p(titreRun("Comment candidater ?", 29, C.blanc), { spacing: { after: 30 } }),
    p([g("Nous étudions toutes les candidatures", { size: 16, color: C.blanc }), t(" et nous nous engageons à répondre à chacune.", { size: 16, color: C.creme })], { spacing: { after: 140 } }),
    grille(COL_INFO, [
      info(0, "ico_lieu.png", "Lieu et prise de poste", "Grenoble (38)", []),
      info(1, "ico_contrat.png", "Contrat", "CDI · statut cadre", ["Avocat(e) salarié(e), forfait jours (218), association future"]),
      info(2, "ico_processus.png", "Processus de recrutement", "4 étapes", ["Un échange téléphonique, puis trois entretiens au cabinet"]),
      info(3, "ico_candidature_rouge.png", "Candidature", "CV et lettre de motivation", ["recrutement@", "victimesetprejudices.fr"]),
    ]),
    p([], { spacing: { after: dxa(5) } }),
    lignePied(C.creme, "2 / 2"),
  ],
});

// ---------------------------------------------------------------------------
// Ouverture : le titre et la raison d'être du poste, en blanc sur fond ardoise
// ---------------------------------------------------------------------------
const RETRAIT = dxa(52); // laisse la place à la grande feuille

const ouverture = [
  p(image("logo_reserve.png", 32), { spacing: { after: dxa(5) } }),
  p(surtitre("OFFRE D'EMPLOI  ·  CDI", C.orange, 15), { spacing: { after: 40 } }),
  p([titreRun("Avocat(e) ", 58, C.blanc), titreRun("salarié(e)", 58, C.orange)], { spacing: { after: 110, line: 240 } }),
  p(t("Nous recherchons aujourd'hui un(e) avocat(e) démontrant un fort leadership et une capacité à prendre à terme le relais dans l'animation du cabinet.", { size: 20, color: C.blanc }),
    { indent: { right: RETRAIT }, spacing: { after: 100, line: 280 } }),
  p(titreRun("Ce poste est créé dans une perspective rapide d'association.", 24, C.orange),
    { indent: { left: dxa(3.5), right: RETRAIT }, border: { left: { style: BorderStyle.SINGLE, size: 24, color: C.orange, space: 8 } }, spacing: { after: 140, line: 255 } }),
  p([
    surtitre("GRENOBLE (38)", C.creme, 13), surtitre("   ·   CDI   ·   STATUT CADRE   ·   ", C.creme, 13),
    surtitre("PERSPECTIVE D'ASSOCIATION", C.orange, 13),
  ]),
  espace(15),
];

// ---------------------------------------------------------------------------
// Sections
// ---------------------------------------------------------------------------
const cabinet = section({
  numero: "01",
  appel: [
    p(titreRun("« Défendre les victimes n'est pas seulement un métier. C'est d'abord notre engagement. »", 18, C.ardoise), { spacing: { after: 70, line: 245 } }),
    p(t("Hervé Gerbi, avocat fondateur", { size: 14, color: C.secondaire }), { spacing: { after: 0 } }),
  ],
  surtitreTexte: "LE CABINET ET LE CONTEXTE",
  titre: "Un cabinet dédié aux victimes",
  contenu: [
    paragraphe([
      g("Victimes & Préjudices Avocats"), " est un cabinet grenoblois et annecien ",
      g("exclusivement dédié à la défense des victimes"),
      " : accidents de la route, responsabilité médicale, accidents corporels et maladies du travail, accidents de la vie, droit pénal des victimes. Nous accompagnons chaque jour les victimes et leurs familles ",
      g("jusqu'à leur complète indemnisation"), ".",
    ]),
  ],
});

const missions = section({
  numero: "02",
  appel: question("Prêt(e) à relever de nouveaux défis ?"),
  surtitreTexte: "VOS MISSIONS",
  titre: "De la consultation à l'indemnisation",
  contenu: [
    ["Piloter", "en autonomie un portefeuille de dossiers jusqu'à l'indemnisation définitive",
      "Construire", "des stratégies d'indemnisation sur mesure : analyse des pièces médicales et juridiques, évaluation et chiffrage des préjudices"],
    ["Rédiger", "les actes : assignations, conclusions, consultations, notes de synthèse",
      "Préparer et conduire", "les expertises médicales amiables et judiciaires, en lien étroit avec les médecins de recours et les autres experts"],
    ["Plaider", "devant les juridictions civiles, administratives et pénales",
      "Porter la relation client", "accompagner les victimes et leurs proches à chaque étape, en interlocuteur ou interlocutrice de référence"],
    ["Développer", "les relations avec les prescripteurs, la visibilité, les relations presse et de nouveaux axes de pratique",
      "Faire évoluer", "nos méthodes : structuration des process, outils numériques, intelligence artificielle, montée en compétence de l'équipe"],
  ].flatMap(([t1, d1, t2, d2], i) => [
    ...(i ? [espace(2.5)] : []),
    cartes(colonnes(2, PRINCIPALE), [mission(t1, d1), mission(t2, d2)]),
  ]),
});

const COL_LISTES = colonnes(2, PRINCIPALE);
const profil = section({
  nouvellePage: true,
  numero: "03",
  appel: question("Vous vous projetez dans un projet d'association ?"),
  surtitreTexte: "PROFIL RECHERCHÉ",
  titre: "Formation et expérience",
  contenu: [
    cartes(colonnes(3, PRINCIPALE), [
      tuile("CAPA", "et inscription à un barreau français", C.ardoise, C.orange, C.blanc),
      tuile("5 ans minimum", "de pratique en cabinet, avec une réelle exposition au contentieux et à la relation client", C.ardoise, C.orange, C.blanc),
      tuile("+ Spécialisation", "en droit du dommage corporel, en responsabilité médicale ou en droit de la santé serait un plus", C.ardoise, C.orange, C.blanc),
    ]),
    p([g("À défaut", { size: 17 }), t(", votre capacité à vous approprier rapidement la matière et à prendre le relais compte davantage qu'une spécialisation déjà acquise.", { size: 17 })],
      { alignment: AlignmentType.JUSTIFIED, spacing: { before: dxa(3.5), after: dxa(3.5), line: 265 } }),
    grille(COL_LISTES, [
      cellule(COL_LISTES[0], [carteListe(COL_LISTES[0], "COMPÉTENCES TECHNIQUES", [
        ["Responsabilité civile : ", "solide maîtrise du droit de la responsabilité civile et des mécanismes d'indemnisation."],
        ["Actes et plaidoirie : ", "aisance en rédaction d'actes et à la plaidoirie."],
        ["Pièces médicales : ", "capacité à travailler sur pièces médicales et à dialoguer avec des experts."],
        ["Numérique et IA : ", "appétence réelle pour les outils numériques et l'innovation juridique (digitalisation, IA)."],
      ])]),
      cellule(COL_LISTES[1], []),
      cellule(COL_LISTES[2], [carteListe(COL_LISTES[2], "QUALITÉS PERSONNELLES", [
        ["Leadership : ", "vous savez entraîner une équipe, arbitrer et décider."],
        ["Esprit entrepreneurial : ", "vous prenez des initiatives et vous inscrivez dans une logique de développement."],
        ["Excellente communication : ", "à l'écrit comme à l'oral, devant un tribunal comme face à des victimes éprouvées."],
        ["Sens affirmé de la relation client : ", "écoute, empathie, humanité."],
        ["Autonomie, rigueur et sens du collectif", ", dans un environnement exigeant et bienveillant."],
      ])]),
    ]),
  ],
});

const offre = section({
  numero: "04",
  appel: question("Une ambition à la hauteur de la vôtre ?"),
  surtitreTexte: "CE QUE NOUS VOUS OFFRONS",
  titre: "Une perspective d'association",
  contenu: [
    paragraphe(["Une ", g("perspective d'association jalonnée dans le temps"), ", et un périmètre de responsabilités large, avec une vraie latitude de décision et une exposition client directe."], dxa(3.5)),
    cartes(colonnes(2, PRINCIPALE), [
      tuile("218 jours", "CDI, statut cadre, forfait annuel ; rémunération fixe selon profil et expérience", C.rouge, C.blanc, C.blanc, 26),
      tuile("PEE et PER", "avec abondement du cabinet, en plus des tickets restaurant", C.rouge, C.blanc, C.blanc, 26),
    ]),
    espace(2.5),
    cartes(colonnes(3, PRINCIPALE), [
      tuile("Fort enjeu humain", "des dossiers techniques, au service exclusif des victimes", C.creme, C.ardoise, C.secondaire, 20),
      tuile("Taille humaine", "un cabinet équipé d'outils numériques performants et engagé dans l'innovation", C.creme, C.ardoise, C.secondaire, 20),
      tuile("Au cœur des Alpes", "Grenoble et son cadre de vie montagneux", C.creme, C.ardoise, C.secondaire, 20),
    ]),
  ],
});

// ---------------------------------------------------------------------------
// Document
// ---------------------------------------------------------------------------
const policesIncorporees = POLICES ? [
  ["Poppins SemiBold", "Poppins_600SemiBold.ttf"],
  ["Poppins Medium", "Poppins_500Medium.ttf"],
  ["Open Sans", "OpenSans_400Regular.ttf"],
  ["Open Sans SemiBold", "OpenSans_600SemiBold.ttf"],
].map(([name, fichier]) => ({ name, data: fs.readFileSync(path.join(POLICES, fichier)), characterSet: CharacterSet.ANSI })) : undefined;

const doc = new Document({
  creator: "Victimes & Préjudices Avocats",
  title: "Offre d'emploi – Avocat(e) salarié(e)",
  fonts: policesIncorporees,
  styles: { default: { document: { run: { font: TEXTE, size: 18, color: C.texte } } } },
  numbering: {
    config: [{
      reference: "puceRouge",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "●", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 250, hanging: 250 } }, run: { color: C.rouge, size: 12 } },
      }],
    }],
  },
  sections: [{
    properties: {
      titlePage: true,
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: dxa(12), bottom: dxa(14), left: dxa(16), right: dxa(16), header: dxa(5), footer: dxa(6) },
      },
    },
    headers: { first: enTetePremiere, default: enTeteSuite },
    footers: { first: piedPremiere, default: piedSuite },
    children: [...ouverture, ...cabinet, separateur(), ...missions, ...profil, separateur(), ...offre],
  }],
});

// Clés de polices incorporées en hexadécimal majuscule (schéma OOXML)
async function normaliserClesPolices(buffer) {
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(buffer);
  const table = zip.file("word/fontTable.xml");
  if (!table) return buffer;
  const xml = (await table.async("string")).replace(/w:fontKey="(\{[^"]+\})"/g, (_, cle) => `w:fontKey="${cle.toUpperCase()}"`);
  zip.file("word/fontTable.xml", xml);
  return zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}

Packer.toBuffer(doc).then(normaliserClesPolices).then((buffer) => {
  fs.writeFileSync(SORTIE, buffer);
  console.log(`Offre générée : ${SORTIE}`);
});
