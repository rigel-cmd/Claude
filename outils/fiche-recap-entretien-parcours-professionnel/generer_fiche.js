// Génère la fiche d'information sur les quatre dispositifs d'évolution professionnelle
// (CEP, VAE, CPF, dotation du cabinet), remise au collaborateur lors de l'entretien de
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
  .replace(/(\d) (?=\d)/g, "$1" + NBSP);
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

// ---------------------------------------------------------------------------
// Grille éditoriale des modules : colonne d'appel (pastille + question) et colonne
// principale (surtitre, titre, accroche, faits). Une seule surface (crème clair) ;
// la couleur de chaque dispositif ne sert qu'aux accents.
// ---------------------------------------------------------------------------
const CREME_CLAIR = "FDF8E6";
const FILET = "DCD8D2";
const RAIL = dxa(36);
const ENTRE = dxa(6);
const PRINCIPALE = LARGEUR - RAIL - ENTRE; // 136 mm

function module({ pastille, question, numero, surtitreTexte, couleur, titre, accroche, contenu, nouvellePage = false }) {
  return [
    new Paragraph({ children: [], pageBreakBefore: nouvellePage, spacing: { after: 0, line: 40, lineRule: "exact" } }),
    grille([RAIL, ENTRE, PRINCIPALE], [
      cellule(RAIL, [
        p(image(pastille, 12), { spacing: { after: dxa(3.5) } }),
        p(titreRun(question, 18, C.ardoise), { spacing: { after: 0, line: 250 }, indent: { right: dxa(2) } }),
      ]),
      cellule(ENTRE, []),
      cellule(PRINCIPALE, [
        p(surtitre(`${numero}  ·  ${surtitreTexte}`, couleur, 13), { spacing: { after: 30 } }),
        p(titreRun(titre, 31, C.ardoise), { spacing: { after: 90, line: 240 } }),
        p([].concat(accroche), { spacing: { after: dxa(3.5), line: 276 } }),
        ...contenu,
      ]),
    ]),
  ];
}

const separateur = () => p([], {
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: FILET, space: 1 } },
  spacing: { before: dxa(4.5), after: dxa(5.5) },
});

// Carte : fond crème clair, filet supérieur dans la couleur du dispositif
const carte = (couleur, enfants, marges = { top: 110, bottom: 115, left: 170, right: 170 }) => ({
  fond: CREME_CLAIR,
  bordures: { top: { style: BorderStyle.SINGLE, size: 12, color: couleur } },
  marges,
  enfants,
});

// Chiffre clé
const fait = (couleur, valeur, libelle) => carte(couleur, [
  p(titreRun(valeur, 30, couleur), { spacing: { after: 30, line: 240 } }),
  p(t(libelle, { size: 15, color: C.secondaire }), { spacing: { after: 0, line: 245 } }),
]);

const accroche = (...morceaux) => morceaux.map((m) => (typeof m === "string" ? t(m, { size: 19 }) : m));
const fort = (texte) => g(texte, { size: 19 });

const ligneIcone = (icone, enfants, after = 45) =>
  p([image(icone, 3.2), t("  ", { size: 15 }), ...[].concat(enfants)], { spacing: { after, line: 245 } });

const contact = (etiquette, nom, telephone, horaires, site, complement) => carte(C.rouge, [
  p(surtitre(etiquette, C.rouge, 12), { spacing: { after: 20 } }),
  p(titreRun(nom, 23, C.ardoise), { spacing: { after: 70 } }),
  ligneIcone("ico_tel.png", titreRun(telephone, 21, C.ardoise)),
  ligneIcone("ico_horaires.png", t(horaires, { size: 15 })),
  ligneIcone("ico_web.png", g(site, { size: 15 })),
  ligneIcone("ico_lieu.png", t(complement, { size: 15 }), 0),
], { top: 140, bottom: 150, left: 180, right: 160 });

const note = (enfants, before = dxa(3)) => p(enfants, { spacing: { before, after: 0, line: 250 } });

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

const lignesSources = (avecLisere) => p([
  ...(avecLisere ? [imageFlottante("lisere.png", 0, 297 - 2.2, 210)] : []),
  t(`À jour au ${DATE_MAJ} – sources : apec.fr, ara.avenir-actifs.org, vae.gouv.fr, moncompteformation.gouv.fr, opcoep.fr, enadep.com. Montants et règles susceptibles d'évoluer.`, { size: 12, color: C.secondaire }),
  new TextRun({ children: ["\t", PageNumber.CURRENT, " / ", PageNumber.TOTAL_PAGES], font: TITRE_M, size: 13, color: C.ardoise }),
], { tabStops: [{ type: TabStopType.RIGHT, position: LARGEUR }] });

const piedPremiere = new Footer({ children: [lignesSources(true)] });

// Verso : le pied de page porte le mémo, posé sur le bandeau crème de clôture
const H_BANDEAU_BAS = 72;
const COL_MEMO = Array(4).fill(LARGEUR / 4);
const entreeMemo = (i, pastille, couleur, nom, lien, details) => cellule(COL_MEMO[i], [
  p(image(pastille, 8.5), { spacing: { after: 70 } }),
  p(titreRun(nom, 17, C.ardoise), { spacing: { after: 30, line: 235 } }),
  p(g(lien, { size: 15, color: couleur }), { spacing: { after: 20, line: 235 } }),
  ...[].concat(details).map((d) => p(t(d, { size: 14, color: C.secondaire }), { spacing: { after: 0, line: 235 } })),
], {
  marges: { top: 0, bottom: 0, left: i === 0 ? 0 : 170, right: 120 },
  bordures: i === 0 ? {} : { left: { style: BorderStyle.SINGLE, size: 4, color: "E3D7A8" } },
});

const piedSuite = new Footer({
  children: [
    p([
      imageFlottante("bandeau_bas.png", 0, 297 - H_BANDEAU_BAS, 210),
      surtitre("EN RÉSUMÉ", C.rouge, 13),
    ], { spacing: { after: 10 } }),
    p(titreRun("Où vous informer ?", 29, C.ardoise), { spacing: { after: 130 } }),
    grille(COL_MEMO, [
      entreeMemo(0, "pastille_cep.png", C.rouge, "Conseil en évolution professionnelle", "mon-cep.org", ["Apec 0 809 361 212", "Avenir Actifs 09 72 01 02 03"]),
      entreeMemo(1, "pastille_vae.png", C.orangeTexte, "Validation des acquis de l'expérience", "vae.gouv.fr", "Candidature et suivi de votre parcours en ligne"),
      entreeMemo(2, "pastille_cpf.png", C.vertTexte, "Compte personnel de formation", "moncompteformation.gouv.fr", "Site et application Mon Compte Formation"),
      entreeMemo(3, "pastille_dot.png", C.ardoise, "Dotation du cabinet", "Votre responsable au cabinet", ["Formations métier :", "enadep.com"]),
    ]),
    p([], { spacing: { after: dxa(5) } }),
    lignesSources(true),
  ],
});

// ---------------------------------------------------------------------------
// Recto
// ---------------------------------------------------------------------------
const RETRAIT_TITRE = dxa(55); // laisse la place à la grande feuille du bandeau
const sep = () => surtitre("   ·   ", C.gris, 13);

const ouverture = [
  p(image("logo.png", 34), { spacing: { after: dxa(5) } }),
  p(surtitre("FICHE D'INFORMATION", C.rouge, 15), { spacing: { after: 50 } }),
  p([
    titreRun("Faire évoluer votre", 50, C.ardoise),
    titreRun("parcours professionnel", 50, C.rouge, { break: 1 }),
  ], { spacing: { after: 110, line: 226 }, indent: { right: RETRAIT_TITRE } }),
  p(t("Quatre dispositifs à connaître", { size: 21 }), { spacing: { after: 70 }, indent: { right: RETRAIT_TITRE } }),
  p([
    surtitre("CEP", C.rouge, 13), sep(), surtitre("VAE", C.orangeTexte, 13), sep(),
    surtitre("CPF", C.vertTexte, 13), sep(), surtitre("DOTATION DU CABINET", C.ardoise, 13),
  ], { indent: { right: RETRAIT_TITRE } }),
  espace(13),
];

const cep = module({
  pastille: "pastille_cep.png",
  question: "Vous vous interrogez sur votre avenir professionnel ?",
  numero: "01", surtitreTexte: "ÊTRE ACCOMPAGNÉ(E)", couleur: C.rouge,
  titre: "Le conseil en évolution professionnelle",
  accroche: accroche("Un service public ", fort("gratuit, confidentiel et personnalisé"),
    " pour faire le point sur vos compétences, clarifier un projet, préparer une reconversion ou choisir une formation. Vous le sollicitez à votre initiative, ",
    fort("sans l'accord du cabinet"), "."),
  contenu: [
    cartes(colonnes(2, PRINCIPALE), [
      contact("CADRES · AVOCAT(E)S SALARIÉ(E)S", "Apec", "0 809 361 212", "Du lundi au vendredi, 9 h – 19 h", "apec.fr", "Plus de 600 consultants en France"),
      contact("TOUS LES SALARIÉ(E)S · AURA", "Mon CEP · Avenir Actifs", "09 72 01 02 03", "Lun.–ven. 8 h – 19 h, sam. 9 h – 12 h", "ara.avenir-actifs.org", "130 lieux, dont Grenoble et Annecy"),
    ]),
    note([
      g("Comment ? ", { size: 16 }),
      t("Entretiens sur place ou à distance, ateliers, immersions : vous repartez avec un diagnostic et un plan d'action.", { size: 16 }),
    ]),
    note([
      g("Autres situations ", { size: 14, color: C.secondaire }),
      t("moins de 26 ans › Mission locale  ·  situation de handicap › Cap emploi  ·  autre région › ", { size: 14, color: C.secondaire }),
      g("mon-cep.org", { size: 14, color: C.secondaire }),
    ], dxa(1.5)),
  ],
});

const vae = module({
  pastille: "pastille_vae.png",
  question: "Votre expérience vaut un diplôme que vous n'avez pas ?",
  numero: "02", surtitreTexte: "FAIRE RECONNAÎTRE SON EXPÉRIENCE", couleur: C.orangeTexte,
  titre: "La validation des acquis de l'expérience",
  accroche: accroche("Obtenez ", fort("tout ou partie d'un diplôme, d'un titre ou d'un CQP"),
    " grâce à votre expérience professionnelle, bénévole ou syndicale, ", fort("sans condition de durée"), "."),
  contenu: [
    cartes(colonnes(2, PRINCIPALE), [
      fait(C.orangeTexte, "48 h", "de congé VAE sur votre temps de travail, rémunération maintenue"),
      fait(C.orangeTexte, "6 à 8 mois", "de parcours pour certains diplômes"),
    ]),
    espace(3),
    cartes(colonnes(2, PRINCIPALE), [
      fait(C.orangeTexte, "1 référent", "l'architecte accompagnateur de parcours, du diagnostic jusqu'au jury"),
      fait(C.orangeTexte, "CPF", "pour financer, avec l'appui possible du cabinet, de l'OPCO EP ou de la Région"),
    ]),
    note([
      g("Comment ? ", { size: 16 }),
      t("Candidature en ligne sur ", { size: 16 }), g("vae.gouv.fr", { size: 16 }),
      t(" ; congé VAE à demander par écrit au cabinet.", { size: 16 }),
    ]),
  ],
});

// ---------------------------------------------------------------------------
// Verso
// ---------------------------------------------------------------------------
const cpf = module({
  nouvellePage: true,
  pastille: "pastille_cpf.png",
  question: "Vous avez un projet de formation ?",
  numero: "03", surtitreTexte: "SE FORMER", couleur: C.vertTexte,
  titre: "Le compte personnel de formation",
  accroche: accroche("Votre compte est crédité ", fort("chaque année, automatiquement"),
    ", tant que vous travaillez. Consultez vos droits et choisissez une formation certifiante sur ",
    fort("moncompteformation.gouv.fr"), " ou l'application Mon Compte Formation."),
  contenu: [
    cartes(colonnes(3, PRINCIPALE), [
      fait(C.vertTexte, "500 €", "par an, jusqu'à 5 000 € – salarié(e) à mi-temps ou plus"),
      fait(C.vertTexte, "800 €", "par an, jusqu'à 8 000 € – sans diplôme de niveau CAP-BEP, ou travailleur handicapé bénéficiaire de l'OETH"),
      fait(C.vertTexte, "150 €", "de participation par formation depuis le 2 avril 2026, non due si le cabinet cofinance"),
    ]),
    espace(3.5),
    puce("puceVert", [g("Plafonds depuis le 20 février 2026 : ", { size: 16 }), t("bilan de compétences 1 600 € (un tous les 5 ans), certifications du Répertoire spécifique 1 500 €, permis B 900 € (avec un cofinancement).", { size: 16 })]),
    puce("puceVert", [g("Hors temps de travail : ", { size: 16 }), t("aucune autorisation. ", { size: 16 }), g("Sur le temps de travail : ", { size: 16 }), t("accord du cabinet à demander 60 jours avant (120 jours si la formation dure 6 mois ou plus) ; sans réponse sous 30 jours, la demande est acceptée.", { size: 16 })]),
  ],
});

const dotation = module({
  pastille: "pastille_dot.png",
  question: "Ce projet sert aussi le cabinet ?",
  numero: "04", surtitreTexte: "CONSTRUIRE ENSEMBLE", couleur: C.ardoise,
  titre: "La dotation du cabinet",
  accroche: accroche("Le cabinet peut ", fort("abonder votre CPF"),
    " pour financer tout ou partie d'une formation ", fort("définie ensemble"),
    ", qui répond à vos souhaits et à ses besoins."),
  contenu: [
    cartes(colonnes(2, PRINCIPALE), [
      fait(C.ardoise, "En premier", "la dotation du cabinet est utilisée avant vos droits CPF, qui complètent si nécessaire ; vous en êtes averti(e) sur votre compte"),
      fait(C.ardoise, "150 € non dus", "la participation obligatoire n'est pas demandée en cas de cofinancement ; l'OPCO EP ou la Région peuvent aussi compléter"),
    ]),
    note([
      g("Formations métier : ", { size: 16 }),
      t("l'ENADEP (", { size: 16 }), g("enadep.com", { size: 16 }),
      t(") forme le personnel des cabinets d'avocats ; ses formations peuvent être prises en charge par le cabinet ou l'OPCO EP, selon ses règles.", { size: 16 }),
    ], dxa(3.5)),
    p([
      image("ico_idee.png", 7),
      t("   ", { size: 16 }),
      g("Un projet de formation en tête ? ", { size: 17, color: C.ardoise }),
      t("Parlez-en à votre responsable au cabinet.", { size: 17 }),
    ], { spacing: { before: dxa(3.5), after: 0, line: 250 } }),
  ],
});

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
    footers: { first: piedPremiere, default: piedSuite },
    children: [...ouverture, ...cep, separateur(), ...vae, ...cpf, separateur(), ...dotation],
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
