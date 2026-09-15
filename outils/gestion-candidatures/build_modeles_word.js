// Génère les quatre modèles Word utilisés par le module VP_Candidatures.bas
// Les balises {{...}} sont remplacées automatiquement par la macro.
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, Header, Footer, convertMillimetersToTwip
} = require('/tmp/node_modules/docx');

const NAVY = '12355B', GREY = '5A6B7B', GOLD = 'B8912A', INK = '1F2933';
const FONT = 'Arial';
const CONTENT = 9072;                       // largeur utile en DXA (A4, marges 2,5 cm)

const r = (text, o = {}) => new TextRun({
  text, font: FONT, size: (o.size || 21), bold: !!o.bold, italics: !!o.it,
  color: o.color || INK, allCaps: !!o.caps, break: o.break || 0
});
const p = (text, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.LEFT,
  spacing: { before: o.before || 0, after: o.after === undefined ? 120 : o.after, line: o.line || 260 },
  indent: o.indent,
  border: o.border,
  children: Array.isArray(text) ? text : [r(text, o)]
});
const vide = (n = 1) => Array.from({ length: n }, () => p('', { after: 0 }));

const enTete = () => new Header({
  children: [
    p('{{CABINET}}', { bold: true, size: 26, color: NAVY, after: 20 }),
    p('{{ADRESSE}}', { size: 16, color: GREY, after: 0 }),
    p('Tél. {{TELEPHONE}}  —  {{EMAIL_RH}}  —  {{SITE}}', {
      size: 16, color: GREY, after: 160,
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 6 } }
    })
  ]
});
const pied = (texte) => new Footer({
  children: [p(texte, { size: 14, color: GREY, align: AlignmentType.CENTER, after: 0 })]
});

const cell = (children, o = {}) => new TableCell({
  width: { size: o.w, type: WidthType.DXA },
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
  margins: { top: 60, bottom: 60, left: 110, right: 110 },
  children
});
const tableau = (widths, rows) => new Table({
  columnWidths: widths,
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  borders: {
    top: { style: BorderStyle.SINGLE, size: 2, color: 'C5D0DB' },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: 'C5D0DB' },
    left: { style: BorderStyle.SINGLE, size: 2, color: 'C5D0DB' },
    right: { style: BorderStyle.SINGLE, size: 2, color: 'C5D0DB' },
    insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: 'C5D0DB' },
    insideVertical: { style: BorderStyle.SINGLE, size: 2, color: 'C5D0DB' }
  },
  rows
});
const ligne2 = (label, valeur) => new TableRow({
  children: [
    cell([p(label, { size: 19, bold: true, color: NAVY, after: 0 })], { w: 3200, fill: 'F4F7FB' }),
    cell([p(valeur, { size: 19, after: 0 })], { w: 5872 })
  ]
});
const titreSection = (t) => p(t, {
  bold: true, size: 21, color: NAVY, caps: true, before: 240, after: 120,
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: GOLD, space: 4 } }
});

const doc = (children, piedTexte) => new Document({
  creator: 'Cabinet Victimes & Préjudices',
  description: 'Modèle de document — gestion des candidatures',
  styles: { default: { document: { run: { font: FONT, size: 21, color: INK } } } },
  sections: [{
    properties: { page: { margin: {
      top: convertMillimetersToTwip(22), bottom: convertMillimetersToTwip(20),
      left: convertMillimetersToTwip(25), right: convertMillimetersToTwip(25)
    } } },
    headers: { default: enTete() },
    footers: { default: pied(piedTexte) },
    children
  }]
});

const blocDestinataire = () => [
  p('{{CIVILITE}} {{PRENOM}} {{NOM}}', { align: AlignmentType.RIGHT, after: 0, size: 21 }),
  p('{{VILLE}}', { align: AlignmentType.RIGHT, after: 0, size: 21, color: GREY }),
  p('{{EMAIL}}', { align: AlignmentType.RIGHT, after: 240, size: 19, color: GREY })
];
const dateLieu = () => p('{{LIEU_SIGNATURE}}, le {{DATE_DU_JOUR}}', { align: AlignmentType.RIGHT, after: 320 });
const signature = () => [
  p('', { after: 200 }),
  p('{{SIGNATAIRE}}', { align: AlignmentType.RIGHT, bold: true, after: 0 }),
  p('{{FONCTION}}', { align: AlignmentType.RIGHT, color: GREY, size: 19, after: 0 })
];
const PIED_RGPD = 'Données traitées aux seules fins du recrutement et conservées {{DUREE_CONSERVATION}} ans à compter du dernier contact — droits exerçables à {{EMAIL_RH}}';

/* ------------------------------------------------ 1. FICHE CANDIDAT */
const CRITERES = [
  'Parcours et expérience en dommage corporel',
  'Maîtrise de la nomenclature Dintilhac et de la procédure d\'indemnisation',
  'Qualités rédactionnelles et argumentation juridique',
  'Relation avec les victimes : écoute, pédagogie, disponibilité',
  'Rigueur, organisation et gestion des délais',
  'Travail en équipe et pratique des outils du cabinet',
  'Motivation pour le cabinet et projet professionnel',
  'Adéquation disponibilité / conditions financières'
];
const fiche = doc([
  p('FICHE CANDIDAT', { bold: true, size: 30, color: NAVY, after: 40 }),
  p('Référence {{ID}}  —  poste de {{POSTE}}', { color: GREY, size: 19, after: 240 }),
  titreSection('Identité et coordonnées'),
  tableau([3200, 5872], [
    ligne2('Nom et prénom', '{{CIVILITE}} {{PRENOM}} {{NOM}}'),
    ligne2('Adresse électronique', '{{EMAIL}}'),
    ligne2('Téléphone', '{{TELEPHONE_CANDIDAT}}'),
    ligne2('Ville', '{{VILLE}}')
  ]),
  titreSection('Candidature'),
  tableau([3200, 5872], [
    ligne2('Poste visé', '{{POSTE}}'),
    ligne2('Reçue le', '{{DATE_RECEPTION}}'),
    ligne2('Origine', '{{SOURCE}}'),
    ligne2('Expérience', '{{EXPERIENCE}} an(s)'),
    ligne2('Formation', '{{DIPLOME}}'),
    ligne2('CAPA / CRFPA', '{{CAPA}}'),
    ligne2('Disponibilité', '{{DISPONIBILITE}}'),
    ligne2('Prétentions', '{{PRETENTIONS}}'),
    ligne2('Responsable du dossier', '{{RESPONSABLE}}'),
    ligne2('Évaluation du dossier', '{{EVALUATION}} / 5')
  ]),
  p('Observations portées au suivi : {{COMMENTAIRES}}', { size: 18, color: GREY, before: 140, after: 0 }),
  titreSection('Grille d\'entretien'),
  p('Entretien du ................................ conduit par ................................................',
    { size: 19, color: GREY, after: 160 }),
  tableau([5000, 1100, 2972], [
    new TableRow({
      tableHeader: true,
      children: [
        cell([p('Critère d\'appréciation', { size: 18, bold: true, color: 'FFFFFF', after: 0 })], { w: 5000, fill: NAVY }),
        cell([p('Note /5', { size: 18, bold: true, color: 'FFFFFF', after: 0, align: AlignmentType.CENTER })], { w: 1100, fill: NAVY }),
        cell([p('Observations', { size: 18, bold: true, color: 'FFFFFF', after: 0 })], { w: 2972, fill: NAVY })
      ]
    }),
    ...CRITERES.map((c) => new TableRow({
      children: [
        cell([p(c, { size: 19, after: 0 })], { w: 5000 }),
        cell([p('', { after: 0 })], { w: 1100 }),
        cell([p('', { after: 0 })], { w: 2972 })
      ]
    }))
  ]),
  titreSection('Conclusion'),
  tableau([3200, 5872], [
    ligne2('Avis', 'Très favorable   ☐        Favorable   ☐        Réservé   ☐        Défavorable   ☐'),
    ligne2('Points forts', ''),
    ligne2('Points de vigilance', ''),
    ligne2('Suite à donner', '')
  ]),
  ...vide(1),
  ...signature()
], PIED_RGPD);

/* ------------------------------------------- 2. CONVOCATION ENTRETIEN */
const convocation = doc([
  ...blocDestinataire(),
  dateLieu(),
  p([r('Nos réf. : ', { bold: true }), r('{{ID}}')], { after: 60 }),
  p([r('Objet : ', { bold: true }), r('entretien — poste de {{POSTE}}')], { after: 320 }),
  p('{{CIVILITE_LONGUE}},', { after: 240 }),
  p('Votre candidature au poste de {{POSTE}}, reçue le {{DATE_RECEPTION}}, a retenu notre attention.', { after: 200 }),
  p('Nous vous proposons de nous rencontrer aux date et heure suivantes :', { after: 160 }),
  tableau([3200, 5872], [
    ligne2('Date', '{{DATE_ENTRETIEN}}'),
    ligne2('Heure', '{{HEURE_ENTRETIEN}}'),
    ligne2('Durée prévue', '{{DUREE_ENTRETIEN}} minutes'),
    ligne2('Modalité', '{{TYPE_ENTRETIEN}}'),
    ligne2('Lieu / lien de connexion', '{{LIEU_ENTRETIEN}}'),
    ligne2('Vous serez reçu(e) par', '{{RESPONSABLE}}')
  ]),
  p('Nous vous remercions de bien vouloir vous munir d\'une pièce d\'identité ainsi que, le cas échéant, de vos justificatifs de diplômes et de vos attestations d\'emploi.',
    { before: 220, after: 200 }),
  p('Si ce créneau ne vous convenait pas, n\'hésitez pas à nous proposer d\'autres disponibilités au {{TELEPHONE}} ou à l\'adresse {{EMAIL_RH}}.', { after: 200 }),
  p('Nous vous prions d\'agréer, {{CIVILITE_LONGUE}}, l\'expression de nos salutations distinguées.', { after: 200 }),
  ...signature()
], PIED_RGPD);

/* ------------------------------------------------- 3. LETTRE DE REFUS */
const refus = doc([
  ...blocDestinataire(),
  dateLieu(),
  p([r('Nos réf. : ', { bold: true }), r('{{ID}}')], { after: 60 }),
  p([r('Objet : ', { bold: true }), r('votre candidature au poste de {{POSTE}}')], { after: 320 }),
  p('{{CIVILITE_LONGUE}},', { after: 240 }),
  p('Nous avons étudié avec attention votre candidature au poste de {{POSTE}}, qui nous est parvenue le {{DATE_RECEPTION}}, et vous remercions de la confiance que vous avez témoignée à notre cabinet.', { after: 200 }),
  p('Nous sommes au regret de ne pouvoir y donner une suite favorable. Cette décision ne remet nullement en cause la qualité de votre parcours ; elle tient à l\'adéquation entre votre profil et les besoins actuels du cabinet.', { after: 200 }),
  p('Nous vous souhaitons une pleine réussite dans la suite de votre parcours professionnel et vous prions d\'agréer, {{CIVILITE_LONGUE}}, l\'expression de nos salutations distinguées.', { after: 200 }),
  ...signature()
], PIED_RGPD);

/* --------------------------------- 4. CONVENTION / PROMESSE D'EMBAUCHE */
const convention = doc([
  ...blocDestinataire(),
  dateLieu(),
  p([r('Nos réf. : ', { bold: true }), r('{{ID}}')], { after: 60 }),
  p([r('Objet : ', { bold: true }), r('proposition d\'engagement — poste de {{POSTE}}')], { after: 320 }),
  p('{{CIVILITE_LONGUE}},', { after: 240 }),
  p('À l\'issue de nos échanges, nous avons le plaisir de vous confirmer notre souhait de vous accueillir au sein du cabinet au poste de {{POSTE}}, aux conditions suivantes :', { after: 200 }),
  tableau([3200, 5872], [
    ligne2('Fonction', '{{POSTE}}'),
    ligne2('Nature de l\'engagement', '[contrat de travail / contrat de collaboration libérale / convention de stage]'),
    ligne2('Date d\'entrée en fonction', '[à compléter]'),
    ligne2('Durée', '[durée indéterminée / durée déterminée jusqu\'au ..............]'),
    ligne2('Lieu d\'exercice', '{{ADRESSE}}'),
    ligne2('Rémunération / rétrocession', '[à compléter]'),
    ligne2('Période d\'essai', '[à compléter]'),
    ligne2('Éléments particuliers', '[à compléter]')
  ]),
  p('La présente proposition est valable jusqu\'au ................................ Elle deviendra définitive après régularisation du contrat correspondant et, le cas échéant, accomplissement des formalités prévues par le règlement intérieur national de la profession d\'avocat.',
    { before: 220, after: 200, size: 19 }),
  p('Nous vous remercions de nous retourner un exemplaire de ce courrier revêtu de votre signature, précédée de la mention « bon pour accord ».', { after: 200 }),
  p('Nous vous prions d\'agréer, {{CIVILITE_LONGUE}}, l\'expression de nos salutations distinguées.', { after: 240 }),
  ...signature(),
  p('', { after: 300 }),
  tableau([4536, 4536], [
    new TableRow({
      children: [
        cell([p('Pour le cabinet', { bold: true, size: 19, after: 240 }), p('', { after: 300 })], { w: 4536, fill: 'F4F7FB' }),
        cell([p('Bon pour accord — {{PRENOM}} {{NOM}}', { bold: true, size: 19, after: 240 }), p('', { after: 300 })], { w: 4536 })
      ]
    })
  ]),
  p('Document à adapter par le cabinet avant envoi. Les mentions entre crochets doivent être complétées ou supprimées.',
    { before: 200, size: 16, color: GREY, it: true })
], PIED_RGPD);

const sortie = process.argv[2] || 'modeles-word';
fs.mkdirSync(sortie, { recursive: true });
const fichiers = [
  ['Fiche_Candidat.docx', fiche],
  ['Convocation_Entretien.docx', convocation],
  ['Lettre_Refus.docx', refus],
  ['Convention_Promesse.docx', convention]
];
(async () => {
  for (const [nom, d] of fichiers) {
    const buf = await Packer.toBuffer(d);
    fs.writeFileSync(path.join(sortie, nom), buf);
    console.log('OK', nom, buf.length, 'octets');
  }
})();
