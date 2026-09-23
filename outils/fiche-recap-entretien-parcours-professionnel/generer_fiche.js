// Génère la fiche récapitulative remise au collaborateur lors de l'entretien de
// parcours professionnel (Word, A4 recto-verso).
//
// Usage : npm install docx && node generer_fiche.js [sortie.docx]

const fs = require("fs");
const {
  AlignmentType, BorderStyle, Document, Footer, Header, HeadingLevel, LevelFormat,
  Packer, PageNumber, Paragraph, ShadingType, Table, TableCell, TableRow, TabStopType,
  TextRun, WidthType, VerticalAlign,
} = require("docx");

const SORTIE = process.argv[2] || "Fiche_recap_entretien_parcours_professionnel.docx";
const DATE_MAJ = "23 septembre 2026";

// Charte (identique à l'outil Excel de suivi)
const POLICE = "Arial";
const MARINE = "1F3864";
const GRIS = "595959";
const COULEURS = { cep: "2E75B6", vae: "548235", cpf: "C55A11", dot: "7030A0" };
const FONDS = { cep: "EAF1FB", vae: "EEF5E9", cpf: "FCEEE4", dot: "F3ECF9", intro: "EEF2F8" };

// A4, marges de 1,5 cm
const LARGEUR_PAGE = 11906;
const MARGE = 850;
const LARGEUR = LARGEUR_PAGE - 2 * MARGE; // 10206

const CORPS = 19; // 9,5 pt (demi-points)
const t = (text, opts = {}) => new TextRun({ text, font: POLICE, size: CORPS, ...opts });
const gras = (text, opts = {}) => t(text, { bold: true, ...opts });

const para = (enfants, opts = {}) =>
  new Paragraph({ children: [].concat(enfants), spacing: { after: 60, line: 264 }, ...opts });

const puce = (enfants) =>
  new Paragraph({
    children: [].concat(enfants),
    numbering: { reference: "puces", level: 0 },
    spacing: { after: 40, line: 259 },
  });

const case_a_cocher = (texte) =>
  new Paragraph({
    children: [t("☐  ", { font: "Segoe UI Symbol", size: 20, color: MARINE }), t(texte)],
    spacing: { after: 50 },
  });

function titreSection(numero, texte, cle, nouvellePage = false) {
  return new Paragraph({
    pageBreakBefore: nouvellePage,
    heading: HeadingLevel.HEADING_1,
    children: [
      new TextRun({ text: `${numero}  `, font: POLICE, size: 26, bold: true, color: COULEURS[cle] }),
      new TextRun({ text: texte, font: POLICE, size: 23, bold: true, color: MARINE }),
    ],
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: COULEURS[cle], space: 2 } },
    spacing: { before: 180, after: 90 },
    keepNext: true,
  });
}

const bordureNulle = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const sansBordure = { top: bordureNulle, bottom: bordureNulle, left: bordureNulle, right: bordureNulle };

// Encadré d'une seule cellule (fond coloré, filet gauche)
function encadre(enfants, fond, filet) {
  return new Table({
    width: { size: LARGEUR, type: WidthType.DXA },
    columnWidths: [LARGEUR],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: LARGEUR, type: WidthType.DXA },
            shading: { fill: fond, type: ShadingType.CLEAR, color: "auto" },
            borders: { ...sansBordure, left: { style: BorderStyle.SINGLE, size: 24, color: filet } },
            margins: { top: 100, bottom: 80, left: 180, right: 180 },
            children: enfants,
          }),
        ],
      }),
    ],
  });
}

const espace = (after = 60) => new Paragraph({ children: [], spacing: { after, line: 120 } });

// ---------------------------------------------------------------------------
// Contenu
// ---------------------------------------------------------------------------
const entete = [
  new Paragraph({
    children: [new TextRun({ text: "Votre entretien de parcours professionnel", font: POLICE, size: 36, bold: true, color: MARINE })],
    spacing: { after: 40 },
  }),
  new Paragraph({
    children: [new TextRun({
      text: "Fiche récapitulative : les dispositifs pour faire le point et construire votre évolution professionnelle",
      font: POLICE, size: 20, italics: true, color: GRIS,
    })],
    spacing: { after: 140 },
  }),
  new Paragraph({
    children: [t("Remise à : "), t("\t"), t("   le : "), t("\t"), t("   par : "), t("\t")],
    tabStops: [
      { type: TabStopType.LEFT, position: 4300, leader: "underscore" },
      { type: TabStopType.LEFT, position: 6400, leader: "underscore" },
      { type: TabStopType.LEFT, position: LARGEUR, leader: "underscore" },
    ],
    spacing: { after: 160 },
  }),
  encadre([
    para([
      t("L'entretien de parcours professionnel est un temps d'échange consacré à "),
      gras("vos perspectives d'évolution"),
      t(" : compétences, qualifications, formation, mobilité, reconversion. "),
      gras("Il ne porte pas sur l'évaluation de votre travail."),
      t(" Il a lieu dans l'année qui suit votre embauche, puis tous les 4 ans, et donne lieu à un compte rendu écrit dont vous recevez une copie."),
    ]),
    para([
      t("À cette occasion, vous êtes informé(e) sur quatre dispositifs, résumés ci-dessous : le "),
      gras("conseil en évolution professionnelle"),
      t(", la "),
      gras("validation des acquis de l'expérience"),
      t(", votre "),
      gras("compte personnel de formation"),
      t(" et les "),
      gras("financements que l'entreprise peut y ajouter"),
      t("."),
    ], { spacing: { after: 0, line: 264 } }),
  ], FONDS.intro, MARINE),
];

// Orientation : quel dispositif pour quel besoin ---------------------------------
const COL_ORIENT = [3402, 3402, 3402];
const carteBesoin = (i, cle, besoin, reponse, renvoi) =>
  new TableCell({
    width: { size: COL_ORIENT[i], type: WidthType.DXA },
    shading: { fill: FONDS[cle], type: ShadingType.CLEAR, color: "auto" },
    borders: {
      ...sansBordure,
      top: { style: BorderStyle.SINGLE, size: 18, color: COULEURS[cle] },
      left: { style: BorderStyle.SINGLE, size: 12, color: "FFFFFF" },
      right: { style: BorderStyle.SINGLE, size: 12, color: "FFFFFF" },
    },
    margins: { top: 80, bottom: 80, left: 140, right: 140 },
    children: [
      new Paragraph({ children: [t(besoin, { italics: true, color: GRIS })], spacing: { after: 40 } }),
      new Paragraph({ children: [gras(reponse, { color: COULEURS[cle], size: 20 })], spacing: { after: 20 } }),
      new Paragraph({ children: [t(renvoi, { color: GRIS, size: 16 })] }),
    ],
  });

const orientation = [
  new Paragraph({
    children: [new TextRun({ text: "Quel dispositif pour quel besoin ?", font: POLICE, size: 21, bold: true, color: MARINE })],
    spacing: { before: 200, after: 80 },
    keepNext: true,
  }),
  new Table({
    width: { size: LARGEUR, type: WidthType.DXA },
    columnWidths: COL_ORIENT,
    rows: [new TableRow({
      cantSplit: true,
      children: [
        carteBesoin(0, "cep", "Vous vous interrogez sur votre avenir professionnel ?", "Le CEP vous aide à y voir clair", "Partie 1"),
        carteBesoin(1, "vae", "Votre expérience vaut un diplôme que vous n'avez pas ?", "La VAE la fait reconnaître", "Partie 2"),
        carteBesoin(2, "cpf", "Vous avez un projet de formation ?", "Votre CPF, complété par l'entreprise", "Parties 3 et 4"),
      ],
    })],
  }),
];

// 1. CEP ----------------------------------------------------------------------
const COL_CEP = [LARGEUR / 2, LARGEUR / 2];
function carteContact(fond, lignes) {
  return new TableCell({
    width: { size: COL_CEP[0], type: WidthType.DXA },
    shading: { fill: fond, type: ShadingType.CLEAR, color: "auto" },
    borders: { ...sansBordure, top: { style: BorderStyle.SINGLE, size: 12, color: COULEURS.cep } },
    margins: { top: 90, bottom: 80, left: 150, right: 150 },
    verticalAlign: VerticalAlign.TOP,
    children: lignes,
  });
}
const ligneContact = (enfants, after = 30) => new Paragraph({ children: [].concat(enfants), spacing: { after } });

const cep = [
  titreSection("1", "Faire le point avec un conseiller : le conseil en évolution professionnelle (CEP)", "cep"),
  puce([gras("Un service public gratuit, confidentiel et personnalisé"), t(", ouvert à tous les actifs. Vous le sollicitez à votre initiative, sans avoir besoin de l'accord de votre employeur.")]),
  puce([gras("Pour "), t("faire le point sur vos compétences, clarifier un projet, préparer une reconversion, choisir une formation et son financement, changer de poste ou créer une activité.")]),
  puce([gras("Comment : "), t("entretiens individuels sur place, par téléphone ou en visio, ateliers collectifs, enquêtes métier et immersions en entreprise. Vous repartez avec un "), gras("diagnostic personnalisé et un plan d'action"), t(".")]),
  espace(40),
  new Table({
    width: { size: LARGEUR, type: WidthType.DXA },
    columnWidths: COL_CEP,
    rows: [new TableRow({
      children: [
        carteContact(FONDS.cep, [
          ligneContact(t("Vous êtes cadre ou jeune diplômé(e)", { italics: true, color: GRIS })),
          ligneContact(gras("Apec", { size: 22, color: MARINE }), 40),
          ligneContact([gras("0 809 361 212"), t(" (service gratuit + prix d'un appel)")]),
          ligneContact(t("Du lundi au vendredi, de 9 h à 19 h")),
          ligneContact([gras("apec.fr"), t(" › Conseil en évolution professionnelle")]),
          ligneContact(t("Plus de 600 consultants en France ; rendez-vous individuels ou collectifs.", { color: GRIS }), 0),
        ]),
        carteContact("F5F8FC", [
          ligneContact(t("Vous êtes salarié(e) du privé ou indépendant(e) en Auvergne-Rhône-Alpes", { italics: true, color: GRIS })),
          ligneContact(gras("Mon CEP par Avenir Actifs", { size: 22, color: MARINE }), 40),
          ligneContact(gras("09 72 01 02 03")),
          ligneContact(t("Du lundi au vendredi de 8 h à 19 h, le samedi de 9 h à 12 h")),
          ligneContact(gras("ara.avenir-actifs.org")),
          ligneContact(t("130 lieux d'accueil dans la région, ou à distance (téléphone, visio, e-mail).", { color: GRIS }), 0),
        ]),
      ],
    })],
  }),
  para([
    gras("Autres situations : ", { color: GRIS, size: 16 }),
    t("moins de 26 ans → Mission locale  ·  personne en situation de handicap → Cap emploi  ·  autre région → ", { color: GRIS, size: 16 }),
    gras("mon-cep.org", { color: GRIS, size: 16 }),
  ], { spacing: { before: 70, after: 0 } }),
];

// 2. VAE ----------------------------------------------------------------------
const vae = [
  titreSection("2", "Faire reconnaître votre expérience : la validation des acquis de l'expérience (VAE)", "vae"),
  puce([t("La VAE permet d'obtenir "), gras("tout ou partie d'une certification professionnelle"), t(" (diplôme, titre, certificat de qualification professionnelle) grâce à l'expérience acquise : professionnelle, bénévole, syndicale…")]),
  puce([gras("Sans condition de durée d'expérience"), t(" : il suffit d'avoir des compétences en lien avec la certification visée.")]),
  puce([t("Sur "), gras("vae.gouv.fr"), t(" (France VAE), créez votre compte et déposez votre candidature en moins de 10 minutes. Un "), gras("architecte accompagnateur de parcours"), t(" vous suit du diagnostic de vos compétences jusqu'au bilan après le jury.")]),
  puce([t("Un parcours peut être réalisé en "), gras("6 à 8 mois"), t(" pour certains diplômes.")]),
  puce([gras("Financement : "), t("vos droits CPF, complétés le cas échéant par votre employeur, votre opérateur de compétences (OPCO) ou la Région.")]),
  puce([gras("Congé VAE : "), t("jusqu'à 48 heures d'absence sur votre temps de travail, avec maintien de votre rémunération, sur demande écrite à votre employeur.")]),
];

// 3. CPF ----------------------------------------------------------------------
const COL_CPF = [6006, 2100, 2100];
const celluleCpf = (texte, i, { entete = false, fond } = {}) =>
  new TableCell({
    width: { size: COL_CPF[i], type: WidthType.DXA },
    shading: fond ? { fill: fond, type: ShadingType.CLEAR, color: "auto" } : undefined,
    borders: {
      ...sansBordure,
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "D9D9D9" },
    },
    margins: { top: 50, bottom: 50, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
      children: [entete ? gras(texte, { color: "FFFFFF", size: 17 }) : (i === 0 ? t(texte) : gras(texte))],
    })],
  });

const cpf = [
  titreSection("3", "Financer une formation : votre compte personnel de formation (CPF)", "cpf", true),
  para(t("Votre compte est crédité en euros chaque année, automatiquement, tant que vous travaillez :")),
  new Table({
    width: { size: LARGEUR, type: WidthType.DXA },
    columnWidths: COL_CPF,
    rows: [
      new TableRow({ tableHeader: true, children: ["Votre situation", "Crédit annuel", "Plafond"].map((x, i) => celluleCpf(x, i, { entete: true, fond: COULEURS.cpf })) }),
      new TableRow({ children: ["Salarié(e) à mi-temps ou plus", "500 €", "5 000 €"].map((x, i) => celluleCpf(x, i, { fond: FONDS.cpf })) }),
      new TableRow({ children: ["Salarié(e) sans diplôme de niveau CAP-BEP, ou bénéficiaire de l'obligation d'emploi des travailleurs handicapés", "800 €", "8 000 €"].map((x, i) => celluleCpf(x, i)) }),
    ],
  }),
  espace(50),
  puce([t("Consultez vos droits et choisissez une formation certifiante sur "), gras("moncompteformation.gouv.fr"), t(" ou l'application Mon Compte Formation.")]),
  puce([gras("Participation obligatoire de 150 €"), t(" (montant 2026) à chaque inscription, "), gras("sauf si votre employeur cofinance la formation"), t(".")]),
  puce([t("Depuis le 20 février 2026, certains usages sont plafonnés : bilan de compétences (1 600 € au maximum, un tous les 5 ans), certifications du Répertoire spécifique (1 500 €), permis B (900 €, uniquement avec un cofinancement).")]),
  puce([gras("Hors temps de travail : "), t("aucune autorisation n'est nécessaire. "), gras("Sur le temps de travail : "), t("demandez l'accord de votre employeur au moins 60 jours avant le début de la formation (120 jours si elle dure 6 mois ou plus) ; sans réponse sous 30 jours, la demande est acceptée.")]),
];

// 4. Dotation employeur -------------------------------------------------------
const dotation = [
  titreSection("4", "Construire un projet avec l'entreprise : la dotation de l'employeur", "dot"),
  puce([t("Votre employeur peut "), gras("abonder votre CPF"), t(" (« dotation ») pour financer tout ou partie d'une formation "), gras("définie ensemble"), t(", qui répond à la fois à vos souhaits et aux besoins de l'entreprise.")]),
  puce([t("Vous êtes averti(e) sur votre compte. Lors de l'inscription, la dotation est utilisée en premier ; vos droits CPF complètent si nécessaire.")]),
  puce([t("Avec un cofinancement de votre employeur, "), gras("vous n'avez pas à payer la participation de 150 €"), t(". D'autres financeurs (OPCO, Région) peuvent aussi compléter.")]),
  puce([t("Votre entretien de parcours professionnel est le bon moment pour en parler et construire ce projet commun.")]),
];

// Prochaines étapes -------------------------------------------------------------
const etapes = [
  espace(120),
  encadre([
    new Paragraph({
      children: [new TextRun({ text: "Mes prochaines étapes", font: POLICE, size: 22, bold: true, color: MARINE })],
      spacing: { after: 90 },
    }),
    case_a_cocher("Prendre rendez-vous avec un conseiller en évolution professionnelle"),
    case_a_cocher("Explorer une VAE sur vae.gouv.fr"),
    case_a_cocher("Consulter mes droits sur moncompteformation.gouv.fr"),
    case_a_cocher("Étudier un projet de formation cofinancé avec l'entreprise"),
    new Paragraph({
      children: [t("☐  ", { font: "Segoe UI Symbol", size: 20, color: MARINE }), t("Autre : "), t("\t")],
      tabStops: [{ type: TabStopType.LEFT, position: LARGEUR - 400, leader: "underscore" }],
      spacing: { after: 140 },
    }),
    new Paragraph({
      children: [gras("Votre contact RH : "), t("\t"), gras("   Tél. / e-mail : "), t("\t")],
      tabStops: [
        { type: TabStopType.LEFT, position: 5000, leader: "underscore" },
        { type: TabStopType.LEFT, position: LARGEUR - 400, leader: "underscore" },
      ],
      spacing: { after: 20 },
    }),
  ], "F2F2F2", MARINE),
  espace(120),
  encadre([
    new Paragraph({
      children: [new TextRun({ text: "Mes notes", font: POLICE, size: 22, bold: true, color: MARINE })],
      spacing: { after: 60 },
    }),
    ...Array.from({ length: 7 }, () => new Paragraph({
      children: [t("\t")],
      tabStops: [{ type: TabStopType.LEFT, position: LARGEUR - 400, leader: "underscore" }],
      spacing: { before: 150, after: 0 },
    })),
  ], "FFFFFF", "BFBFBF"),
];

// ---------------------------------------------------------------------------
// Document
// ---------------------------------------------------------------------------
const doc = new Document({
  creator: "Service RH",
  title: "Fiche récapitulative – Entretien de parcours professionnel",
  styles: {
    default: { document: { run: { font: POLICE, size: CORPS } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: POLICE, size: 23, bold: true, color: MARINE },
        paragraph: { spacing: { before: 180, after: 90 }, outlineLevel: 0 } },
    ],
  },
  numbering: {
    config: [{
      reference: "puces",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 300, hanging: 220 } }, run: { color: MARINE } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: LARGEUR_PAGE, height: 16838 },
        margin: { top: 800, bottom: 760, left: MARGE, right: MARGE, header: 400, footer: 360 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "[Logo et nom de l'entreprise]", font: POLICE, size: 16, color: "A6A6A6", italics: true })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 4, color: "D9D9D9", space: 4 } },
            tabStops: [{ type: TabStopType.RIGHT, position: LARGEUR }],
            children: [
              new TextRun({ text: `Informations à jour au ${DATE_MAJ}. Sources : apec.fr, ara.avenir-actifs.org, vae.gouv.fr, moncompteformation.gouv.fr. Montants et règles susceptibles d'évoluer.`, font: POLICE, size: 13, color: GRIS }),
              new TextRun({ children: ["\t", PageNumber.CURRENT, " / ", PageNumber.TOTAL_PAGES], font: POLICE, size: 13, color: GRIS }),
            ],
          }),
        ],
      }),
    },
    children: [...entete, ...orientation, ...cep, ...vae, ...cpf, ...dotation, ...etapes],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(SORTIE, buffer);
  console.log(`Fiche générée : ${SORTIE}`);
});
