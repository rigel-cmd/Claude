// Génère la fiche d'information sur les quatre dispositifs d'évolution professionnelle
// (CEP, VAE, CPF, dotation de l'employeur), remise au collaborateur lors de l'entretien de
// parcours professionnel : Word A4 recto-verso, charte Victimes & Préjudices Avocats.
//
// Usage :
//   npm install docx
//   node generer_fiche.js [sortie.docx] [dossier_ressources] [dossier_polices]
//
// - dossier_ressources : visuels produits par graphismes.py (défaut : ./ressources) ;
// - dossier_polices (facultatif) : fichiers TTF de Poppins et Open Sans à incorporer au
//   document, pour un rendu identique sur un poste où ces polices ne sont pas installées.

const fs = require("fs");
const path = require("path");
const {
  AlignmentType, BorderStyle, CharacterSet, Document, Footer, Header,
  HorizontalPositionRelativeFrom, ImageRun, LevelFormat, Packer, PageNumber, Paragraph,
  ShadingType, Table, TableCell, TableLayoutType, TableRow, TabStopType, TextRun,
  TextWrappingType, VerticalAlign, VerticalPositionRelativeFrom, WidthType,
} = require("docx");

const SORTIE = process.argv[2] || "Fiche_dispositifs_evolution_professionnelle.docx";
const RES = process.argv[3] || path.join(__dirname, "ressources");
const POLICES = process.argv[4] || null;
const DATE_MAJ = "23 septembre 2026";

// ---------------------------------------------------------------------------
// Charte
// ---------------------------------------------------------------------------
const C = {
  creme: "FAF0C7", rouge: "B52026", orange: "FCAF19", vert: "8EC33F", bleu: "BCDEF0",
  ardoise: "304859", anthracite: "333333", gris: "BEBBBB",
  // déclinaisons : teintes claires pour les fonds, teintes foncées pour le texte coloré
  orangeTexte: "A86A00", vertTexte: "5A8A1F", secondaire: "5F6B73",
  tRouge: "F7E6E6", tOrange: "FFF3DC", tVert: "EEF6E2", tArdoise: "EAEEF0", tBleu: "E3F1F9",
};
const TITRE = "Poppins SemiBold";
const TITRE_M = "Poppins Medium";
const TEXTE = "Open Sans";
const TEXTE_G = "Open Sans SemiBold";

// Unités
const dxa = (mm) => Math.round(mm * 56.6929);
const px = (mm) => (mm / 25.4) * 96;
const emu = (mm) => Math.round(mm * 36000);

// A4, marges latérales de 16 mm
const LARGEUR = 11906 - 2 * dxa(16); // 10092 DXA
const GOUTTIERE = 227; // 4 mm

// ---------------------------------------------------------------------------
// Briques
// ---------------------------------------------------------------------------
const NBSP = "\u00a0";
const typo = (s) => s
  .replace(/'/g, "\u2019")
  .replace(/ ([:;?!])/g, NBSP + "$1")
  .replace(/« /g, "«" + NBSP).replace(/ »/g, NBSP + "»")
  .replace(/(\d) (?=€|h\b|jours|mois|ans|min|salarié|lieux|consultants)/g, "$1" + NBSP)
  .replace(/(\d) (\d{3})/g, "$1" + NBSP + "$2");
const t = (text, o = {}) => new TextRun({ text: typo(text), font: TEXTE, size: 17, color: C.anthracite, ...o });
const g = (text, o = {}) => t(text, { font: TEXTE_G, ...o });
const titreRun = (text, size, color, o = {}) => new TextRun({ text: typo(text), font: TITRE, size, color, ...o });
const surtitre = (text, color, size = 14) =>
  new TextRun({ text: typo(text), font: TITRE_M, size, color, characterSpacing: 30 });

const auto = (spacing) => (spacing && spacing.line && !spacing.lineRule ? { ...spacing, lineRule: "auto" } : spacing);
const p = (children, o = {}) =>
  new Paragraph({ children: [].concat(children), ...o, spacing: auto(o.spacing || { after: 0, line: 259 }) });

function dimensionsPng(fichier) {
  const b = fs.readFileSync(fichier);
  return { l: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}

function image(nom, largeurMm) {
  const { l, h, data } = dimensionsPng(path.join(RES, nom));
  const hauteurMm = (largeurMm * h) / l;
  return new ImageRun({ type: "png", data, transformation: { width: px(largeurMm), height: px(hauteurMm) } });
}

function imageFlottante(nom, xMm, yMm, largeurMm) {
  const { l, h, data } = dimensionsPng(path.join(RES, nom));
  const hauteurMm = (largeurMm * h) / l;
  return new ImageRun({
    type: "png",
    data,
    transformation: { width: px(largeurMm), height: px(hauteurMm) },
    floating: {
      horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: emu(xMm) },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: emu(yMm) },
      behindDocument: true,
      allowOverlap: true,
      lockAnchor: true,
      layoutInCell: false,
      wrap: { type: TextWrappingType.NONE },
    },
  });
}

const AUCUNE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const SANS = { top: AUCUNE, bottom: AUCUNE, left: AUCUNE, right: AUCUNE };
const SANS_TABLE = { ...SANS, insideHorizontal: AUCUNE, insideVertical: AUCUNE };

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

function grille(largeurs, cellules) {
  return new Table({
    width: { size: largeurs.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: largeurs,
    layout: TableLayoutType.FIXED,
    borders: SANS_TABLE,
    rows: [new TableRow({ cantSplit: true, children: cellules })],
  });
}

// Répartit la largeur utile en n cartes séparées par des gouttières
function colonnes(n, largeur = LARGEUR) {
  const utile = largeur - (n - 1) * GOUTTIERE;
  const base = Math.floor(utile / n);
  const cols = Array.from({ length: n }, (_, i) => (i === n - 1 ? utile - base * (n - 1) : base));
  const largeurs = [];
  cols.forEach((c, i) => { largeurs.push(c); if (i < n - 1) largeurs.push(GOUTTIERE); });
  return largeurs;
}

function cartes(largeurs, contenus) {
  const cellules = [];
  let k = 0;
  largeurs.forEach((l, i) => {
    if (i % 2 === 1) {
      cellules.push(cellule(l, []));
      return;
    }
    const c = contenus[k++];
    cellules.push(cellule(l, c.enfants, {
      fond: c.fond,
      bordures: c.bordures,
      marges: c.marges || { top: 150, bottom: 150, left: 170, right: 170 },
    }));
  });
  return grille(largeurs, cellules);
}

const espace = (mm) => new Paragraph({ children: [], spacing: { before: 0, after: 0, line: dxa(mm), lineRule: "exact" } });

const puce = (ref, enfants) =>
  new Paragraph({ children: [].concat(enfants), numbering: { reference: ref, level: 0 }, spacing: { after: 60, line: 259, lineRule: "auto" } });

// En-tête de section : pastille pictogramme + surtitre + titre
function enteteSection(pastille, numero, surtitreTexte, couleurTexte, titre, nouvellePage = false) {
  const l1 = dxa(14);
  return [
    new Paragraph({ children: [], pageBreakBefore: nouvellePage, spacing: { after: 0, line: 60, lineRule: "exact" } }),
    grille([l1, LARGEUR - l1], [
      cellule(l1, [p(image(pastille, 11.5))], { vAlign: VerticalAlign.CENTER }),
      cellule(LARGEUR - l1, [
        p(surtitre(`${numero}  ·  ${surtitreTexte}`, couleurTexte), { spacing: { after: 10 } }),
        p(titreRun(titre, 27, C.ardoise), { spacing: { after: 0, line: 250 } }),
      ], { vAlign: VerticalAlign.CENTER }),
    ]),
    espace(2.5),
  ];
}

// Carte « chiffre clé »
const chiffre = (valeur, libelle, couleur, fond, tailleValeur = 32) => ({
  fond,
  marges: { top: 130, bottom: 130, left: 150, right: 150 },
  enfants: [
    p(titreRun(valeur, tailleValeur, couleur), { spacing: { after: 20, line: 240 } }),
    p(t(libelle, { size: 15, color: C.secondaire }), { spacing: { after: 0, line: 240 } }),
  ],
});

const ligneIcone = (icone, enfants, after = 50) =>
  p([image(icone, 3.4), t("  ", { size: 15 }), ...[].concat(enfants)], { spacing: { after, line: 250 } });

// ---------------------------------------------------------------------------
// En-têtes et pieds de page
// ---------------------------------------------------------------------------
const enTetePremiere = new Header({ children: [p(imageFlottante("bandeau_p1.png", 0, 0, 210))] });
const enTeteSuite = new Header({
  children: [p([
    imageFlottante("bandeau_p2.png", 0, 0, 210),
    surtitre("FAIRE ÉVOLUER VOTRE PARCOURS PROFESSIONNEL  ·  FICHE D'INFORMATION", C.ardoise, 13),
  ], { spacing: { after: dxa(11) } })],
});
const pied = () => new Footer({
  children: [p([
    imageFlottante("lisere.png", 0, 297 - 2.2, 210),
    t(`Informations à jour au ${DATE_MAJ} – sources : apec.fr, ara.avenir-actifs.org, vae.gouv.fr, moncompteformation.gouv.fr. Montants et règles susceptibles d'évoluer.`, { size: 12, color: C.secondaire }),
    new TextRun({ children: ["\t", PageNumber.CURRENT, " / ", PageNumber.TOTAL_PAGES], font: TITRE_M, size: 13, color: C.ardoise }),
  ], { tabStops: [{ type: TabStopType.RIGHT, position: LARGEUR }] })],
});

// ---------------------------------------------------------------------------
// Recto
// ---------------------------------------------------------------------------
const RETRAIT_TITRE = dxa(55); // laisse la place à la grande feuille du bandeau

const ouverture = [
  p(image("logo.png", 34), { spacing: { after: dxa(5) } }),
  p(surtitre("FICHE D'INFORMATION", C.rouge, 15), { spacing: { after: 40 } }),
  p([
    titreRun("Faire évoluer votre", 46, C.ardoise),
    titreRun("parcours professionnel", 46, C.rouge, { break: 1 }),
  ], { spacing: { after: 100, line: 228 }, indent: { right: RETRAIT_TITRE } }),
  p(t("Quatre dispositifs à connaître", { size: 20 }), { indent: { right: RETRAIT_TITRE } }),
  p(surtitre("QUEL DISPOSITIF POUR QUEL BESOIN ?", C.secondaire, 13), { spacing: { before: dxa(15), after: 70 } }),
  cartes(colonnes(4), [
    ["01", C.rouge, C.tRouge, "Vous vous interrogez sur votre avenir professionnel ?", "Le CEP vous aide à y voir clair"],
    ["02", C.orangeTexte, C.tOrange, "Votre expérience vaut un diplôme que vous n'avez pas ?", "La VAE la fait reconnaître"],
    ["03", C.vertTexte, C.tVert, "Vous avez un projet de formation ?", "Votre CPF le finance"],
    ["04", C.ardoise, C.tArdoise, "Ce projet sert aussi l'entreprise ?", "L'employeur peut le cofinancer"],
  ].map(([n, couleur, fond, question, reponse]) => ({
    fond,
    marges: { top: 120, bottom: 130, left: 160, right: 160 },
    enfants: [
      p(titreRun(n, 26, couleur), { spacing: { after: 30, line: 240 } }),
      p(t(question, { size: 15, color: C.secondaire }), { spacing: { after: 40, line: 240 } }),
      p(titreRun(reponse, 19, C.ardoise), { spacing: { after: 0, line: 240 } }),
    ],
  }))),
];

const cep = [
  ...enteteSection("pastille_cep.png", "01", "ÊTRE ACCOMPAGNÉ(E)", C.rouge, "Le conseil en évolution professionnelle (CEP)"),
  cartes(colonnes(3), [
    ["Gratuit et confidentiel", "Un service public ouvert à tous les actifs, à votre initiative, sans l'accord de votre employeur."],
    ["Pour quoi faire ?", "Faire le point sur vos compétences, clarifier un projet, préparer une reconversion, choisir une formation ou changer de poste."],
    ["Comment ?", "Entretiens sur place ou à distance, ateliers, immersions. Vous repartez avec un diagnostic et un plan d'action."],
  ].map(([titre, texte]) => ({
    bordures: { top: { style: BorderStyle.SINGLE, size: 12, color: C.rouge } },
    marges: { top: 90, bottom: 40, left: 0, right: 60 },
    enfants: [
      p(titreRun(titre, 19, C.ardoise), { spacing: { after: 30 } }),
      p(t(texte, { size: 16 }), { spacing: { after: 0, line: 252 } }),
    ],
  }))),
  espace(5),
  cartes(colonnes(2), [
    {
      fond: C.creme,
      marges: { top: 150, bottom: 150, left: 200, right: 200 },
      enfants: [
        p(surtitre("CADRES ET JEUNES DIPLÔMÉ(E)S", C.rouge, 13), { spacing: { after: 20 } }),
        p(titreRun("Apec", 26, C.ardoise), { spacing: { after: 60 } }),
        ligneIcone("ico_tel.png", [titreRun("0 809 361 212", 22, C.ardoise), t("   service gratuit + prix d'un appel", { size: 14, color: C.secondaire })]),
        ligneIcone("ico_horaires.png", t("Du lundi au vendredi, de 9 h à 19 h", { size: 16 })),
        ligneIcone("ico_web.png", [g("apec.fr", { size: 16 }), t(" › Conseil en évolution professionnelle", { size: 16 })]),
        ligneIcone("ico_lieu.png", t("600 consultants, rendez-vous individuels ou collectifs", { size: 16 }), 0),
      ],
    },
    {
      fond: C.tBleu,
      marges: { top: 150, bottom: 150, left: 200, right: 200 },
      enfants: [
        p(surtitre("SALARIÉ(E)S ET INDÉPENDANT(E)S · AURA", C.rouge, 13), { spacing: { after: 20 } }),
        p(titreRun("Mon CEP par Avenir Actifs", 26, C.ardoise), { spacing: { after: 60 } }),
        ligneIcone("ico_tel.png", titreRun("09 72 01 02 03", 22, C.ardoise)),
        ligneIcone("ico_horaires.png", t("Lundi au vendredi 8 h – 19 h, samedi 9 h – 12 h", { size: 16 })),
        ligneIcone("ico_web.png", g("ara.avenir-actifs.org", { size: 16 })),
        ligneIcone("ico_lieu.png", t("130 lieux d'accueil, ou à distance (tél., visio, e-mail)", { size: 16 }), 0),
      ],
    },
  ]),
  p([
    g("Autres situations  ", { size: 14, color: C.secondaire }),
    t("moins de 26 ans › Mission locale   ·   situation de handicap › Cap emploi   ·   autre région › ", { size: 14, color: C.secondaire }),
    g("mon-cep.org", { size: 14, color: C.secondaire }),
  ], { spacing: { before: 80, after: 0 } }),
];

const vae = [
  espace(6),
  ...enteteSection("pastille_vae.png", "02", "FAIRE RECONNAÎTRE SON EXPÉRIENCE", C.orangeTexte, "La validation des acquis de l'expérience (VAE)"),
  cartes(colonnes(4), [
    chiffre("48 h", "de congé VAE sur le temps de travail, rémunération maintenue", C.orangeTexte, C.tOrange),
    chiffre("6 à 8 mois", "de parcours, pour certains diplômes", C.orangeTexte, C.tOrange),
    chiffre("CPF", "pour financer, avec l'appui possible de l'employeur, de l'OPCO ou de la Région", C.orangeTexte, C.tOrange),
    chiffre("1 référent", "l'architecte accompagnateur de parcours, du diagnostic au jury", C.orangeTexte, C.tOrange),
  ]),
  espace(3),
  puce("puceOrange", [t("Obtenez "), g("tout ou partie d'un diplôme, d'un titre ou d'un CQP"), t(" grâce à votre expérience professionnelle, bénévole ou syndicale, "), g("sans condition de durée"), t(". Candidature sur "), g("vae.gouv.fr"), t(" ; congé VAE à demander par écrit à votre employeur.")]),
];

// ---------------------------------------------------------------------------
// Verso
// ---------------------------------------------------------------------------
const cpf = [
  ...enteteSection("pastille_cpf.png", "03", "SE FORMER", C.vertTexte, "Votre compte personnel de formation (CPF)", true),
  cartes(colonnes(3), [
    chiffre("500 €", "crédités par an, jusqu'à 5 000 € – salarié(e) à mi-temps ou plus", C.vertTexte, C.tVert, 36),
    chiffre("800 €", "par an, jusqu'à 8 000 € – sans diplôme de niveau CAP-BEP, ou bénéficiaire de l'obligation d'emploi des travailleurs handicapés", C.vertTexte, C.tVert, 36),
    chiffre("150 €", "de participation par formation en 2026 – non due si votre employeur cofinance", C.vertTexte, C.tVert, 36),
  ]),
  espace(3),
  puce("puceVert", [t("Consultez vos droits et choisissez une formation certifiante sur "), g("moncompteformation.gouv.fr"), t(" ou l'application Mon Compte Formation.")]),
  puce("puceVert", [t("Depuis le 20 février 2026, certains usages sont plafonnés : "), g("bilan de compétences"), t(" (1 600 € au maximum, un tous les 5 ans), "), g("certifications du Répertoire spécifique"), t(" (1 500 €), "), g("permis B"), t(" (900 €, uniquement avec un cofinancement).")]),
  puce("puceVert", [g("Hors temps de travail : "), t("aucune autorisation n'est nécessaire. "), g("Sur le temps de travail : "), t("demandez l'accord de votre employeur au moins 60 jours avant (120 jours si la formation dure 6 mois ou plus) ; sans réponse sous 30 jours, la demande est acceptée.")]),
];

const COL_DOT = [dxa(106), GOUTTIERE * 2, LARGEUR - dxa(106) - GOUTTIERE * 2];
const dotation = [
  espace(9),
  ...enteteSection("pastille_dot.png", "04", "CONSTRUIRE ENSEMBLE", C.ardoise, "La dotation de l'employeur"),
  grille(COL_DOT, [
    cellule(COL_DOT[0], [
      puce("puceArdoise", [t("Votre employeur peut "), g("abonder votre CPF"), t(" (« dotation ») pour financer tout ou partie d'une formation "), g("définie ensemble"), t(", qui répond à vos souhaits et aux besoins de l'entreprise.")]),
      puce("puceArdoise", [t("Vous êtes averti(e) sur votre compte : la dotation est utilisée en premier, vos droits CPF complètent si nécessaire.")]),
      puce("puceArdoise", [t("Avec ce cofinancement, "), g("vous n'avez pas à payer la participation de 150 €"), t(". L'OPCO ou la Région peuvent aussi compléter.")]),
    ]),
    cellule(COL_DOT[1], []),
    cellule(COL_DOT[2], [
      p(image("ico_idee.png", 9), { spacing: { after: 60 } }),
      p(titreRun("Un projet de formation en tête ?", 21, C.ardoise), { spacing: { after: 40, line: 245 } }),
      p(t("Parlez-en à votre responsable ou au service RH : ensemble, vous pouvez en construire le financement.", { size: 16 }), { spacing: { after: 0, line: 252 } }),
    ], { fond: C.creme, marges: { top: 150, bottom: 150, left: 200, right: 200 } }),
  ]),
];

// Mémo final : où s'informer pour chaque dispositif
const COL_MEMO = colonnes(2);
const MARGE_MEMO = 180;
const memo = (pastille, fond, couleur, nom, lien, detail, largeur) => {
  const interieur = largeur - 2 * MARGE_MEMO;
  const l1 = dxa(13);
  return {
    fond,
    marges: { top: 150, bottom: 150, left: MARGE_MEMO, right: MARGE_MEMO },
    enfants: [grille([l1, interieur - l1], [
      cellule(l1, [p(image(pastille, 10))], { vAlign: VerticalAlign.CENTER }),
      cellule(interieur - l1, [
        p(titreRun(nom, 19, C.ardoise), { spacing: { after: 20, line: 240 } }),
        p(g(lien, { size: 17, color: couleur }), { spacing: { after: 10, line: 240 } }),
        p(t(detail, { size: 15, color: C.secondaire }), { spacing: { after: 0, line: 240 } }),
      ], { vAlign: VerticalAlign.CENTER }),
    ])],
  };
};

const ouSInformer = [
  espace(26),
  p(surtitre("EN RÉSUMÉ", C.rouge, 13), { spacing: { after: 10 } }),
  p(titreRun("Où vous informer ?", 27, C.ardoise), { spacing: { after: 110 } }),
  cartes(COL_MEMO, [
    memo("pastille_cep.png", C.tRouge, C.rouge, "Conseil en évolution professionnelle", "mon-cep.org",
      "Apec 0 809 361 212 · Avenir Actifs 09 72 01 02 03", COL_MEMO[0]),
    memo("pastille_vae.png", C.tOrange, C.orangeTexte, "Validation des acquis de l'expérience", "vae.gouv.fr",
      "Candidature en ligne et suivi de votre parcours", COL_MEMO[2]),
  ]),
  espace(4),
  cartes(COL_MEMO, [
    memo("pastille_cpf.png", C.tVert, C.vertTexte, "Compte personnel de formation", "moncompteformation.gouv.fr",
      "Site et application Mon Compte Formation", COL_MEMO[0]),
    memo("pastille_dot.png", C.tArdoise, C.ardoise, "Dotation de l'employeur", "Votre responsable ou le service RH",
      "Pour construire un projet de formation commun", COL_MEMO[2]),
  ]),
];

// ---------------------------------------------------------------------------
// Document
// ---------------------------------------------------------------------------
const puces = (reference, couleur) => ({
  reference,
  levels: [{
    level: 0, format: LevelFormat.BULLET, text: "●", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 260, hanging: 260 } }, run: { color: couleur, size: 12 } },
  }],
});

const policesIncorporees = POLICES ? [
  ["Poppins SemiBold", "Poppins_600SemiBold.ttf"],
  ["Poppins Medium", "Poppins_500Medium.ttf"],
  ["Open Sans", "OpenSans_400Regular.ttf"],
  ["Open Sans SemiBold", "OpenSans_600SemiBold.ttf"],
].map(([name, fichier]) => ({
  name, data: fs.readFileSync(path.join(POLICES, fichier)), characterSet: CharacterSet.ANSI,
})) : undefined;

const doc = new Document({
  creator: "Victimes & Préjudices Avocats",
  title: "Fiche d'information – Quatre dispositifs pour faire évoluer votre parcours professionnel",
  fonts: policesIncorporees,
  styles: { default: { document: { run: { font: TEXTE, size: 17, color: C.anthracite } } } },
  numbering: {
    config: [
      puces("puceOrange", C.orange),
      puces("puceVert", C.vert),
      puces("puceArdoise", C.ardoise),
    ],
  },
  sections: [{
    properties: {
      titlePage: true,
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: dxa(12), bottom: dxa(15), left: dxa(16), right: dxa(16), header: dxa(6), footer: dxa(7) },
      },
    },
    headers: { first: enTetePremiere, default: enTeteSuite },
    footers: { first: pied(), default: pied() },
    children: [...ouverture, ...cep, ...vae, ...cpf, ...dotation, ...ouSInformer],
  }],
});

// Le schéma OOXML impose des clés de police (w:fontKey) en hexadécimal majuscule ; docx les
// écrit en minuscules, ce qui peut déclencher une « réparation » à l'ouverture dans Word.
// La casse n'a pas d'incidence sur le désobscurcissement des polices incorporées.
async function normaliserClesPolices(buffer) {
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(buffer);
  const table = zip.file("word/fontTable.xml");
  if (!table) return buffer;
  const xml = (await table.async("string")).replace(/w:fontKey="(\{[^"]+\})"/g, (_, cle) => `w:fontKey="${cle.toUpperCase()}"`);
  zip.file("word/fontTable.xml", xml);
  return zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}

Packer.toBuffer(doc)
  .then(normaliserClesPolices)
  .then((buffer) => {
    fs.writeFileSync(SORTIE, buffer);
    console.log(`Fiche générée : ${SORTIE}`);
  });
