const test = require('node:test');
const assert = require('node:assert/strict');
const { preetiToUnicode, unicodeToPreeti, looksLikePreeti } = require('../tools/nepali-tools/preeti-unicode-converter/engine.js');

const PAIRS = [
  ['g]kfn', 'नेपाल'],
  [';/sf/', 'सरकार'],
  ['sf7df8f}+', 'काठमाडौं'],
  ['k|wfgdGqL', 'प्रधानमन्त्री'],
  ['lj1fg', 'विज्ञान'],
  ['l;+x', 'सिंह'],
  ['zflGt', 'शान्ति'],
  ['wd{', 'धर्म'],
  ['sfo{', 'कार्य'],
  ['cfly{s', 'आर्थिक'],
  ['lgdf{0f', 'निर्माण'],
  ['If]q', 'क्षेत्र'],
  ['pQ/', 'उत्तर'],
  ['ljBfno', 'विद्यालय'],
  ['>L', 'श्री'],
  ['u\'? ', 'गुरु'],
  ['pmhf{', 'ऊर्जा'],
  ['kmn', 'फल'],
  ['@)*#', '२०८३']
];

test('converts common Preeti words and phrases to Unicode', () => {
  for (const [preeti, unicode] of PAIRS) assert.equal(preetiToUnicode(preeti), unicode, preeti);
});

test('converts Unicode back to Preeti using the matching layout', () => {
  for (const [preeti, unicode] of PAIRS) assert.equal(unicodeToPreeti(unicode), preeti, unicode);
});

test('converts a real-world sentence both ways', () => {
  const preeti = "g]kfn ;/sf/sf k|wfgdGqLn] cfly{s ;'wf/sf] 3f]if0ff ug'{eof] .";
  const unicode = "नेपाल सरकारका प्रधानमन्त्रीले आर्थिक सुधारको घोषणा गर्नुभयो ।";
  assert.equal(preetiToUnicode(preeti), unicode);
  assert.equal(unicodeToPreeti(unicode), preeti);
});

test('round-trips a multi-paragraph Unicode document', () => {
  const paragraph = [
    'काठमाडौं, २०८३ असोज १९ । प्रधानमन्त्रीले आज मन्त्रिपरिषद्को बैठकमा आर्थिक वर्षको बजेट निर्माणबारे छलफल गर्नुभयो ।',
    'विद्यालय क्षेत्रमा राष्ट्रिय शिक्षा नीति लागू गर्ने निर्णय भएको छ । श्री ऊर्जा मन्त्रालयले विद्युत् उत्पादन बढेको जनाएको छ ।',
    'गाउँका किसानहरू खुसी छन्, तर स्वास्थ्य सेवा अझै पुगेको छैन ।'
  ].join('\n');
  assert.equal(preetiToUnicode(unicodeToPreeti(paragraph)), paragraph);
});

test('preserves unknown characters and whitespace', () => {
  assert.equal(preetiToUnicode('g]kfn\n\t ©'), 'नेपाल\n\t ©');
  assert.equal(preetiToUnicode(''), '');
  assert.equal(unicodeToPreeti(''), '');
});

test('recognizes likely Preeti input but not English or Unicode Nepali', () => {
  assert.equal(looksLikePreeti('g]kfn ;/sf/sf k|wfgdGqLn]'), true);
  assert.equal(looksLikePreeti('The government announced reforms.'), false);
  assert.equal(looksLikePreeti('नेपाल सरकार'), false);
  assert.equal(looksLikePreeti(''), false);
});
