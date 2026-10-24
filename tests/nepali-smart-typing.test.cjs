const test = require('node:test');
const assert = require('node:assert/strict');
const smart = require('../tools/nepali-tools/type-nepali/engines/smart-typing.js');

test('lexicon ranks common Nepali words first', () => {
  for (const [roman, expected] of [
    ['namaste', 'नमस्ते'], ['nepal', 'नेपाल'], ['sarkar', 'सरकार'],
    ['kathmandu', 'काठमाडौं'], ['pradhanmantri', 'प्रधानमन्त्री'],
    ['dhanyawad', 'धन्यवाद'], ['shiksha', 'शिक्षा'], ['netaharulai', 'नेताहरूलाई']
  ]) assert.equal(smart.suggest(roman)[0], expected, roman);
});

test('suggestions include alternatives and case endings', () => {
  assert.ok(smart.suggest('sarkar').length >= 3);
  assert.ok(smart.suggest('sarkar').includes('सरकारी'));
  assert.equal(smart.suggest('ankale')[0], 'अंकले');
  assert.equal(smart.suggest('pokharabata')[0], 'पोखराबाट');
});

test('phonetic fallback handles unknown words and ITRANS capitals', () => {
  assert.equal(smart.phonetic('Tuki'), 'टुकी');
  assert.equal(smart.suggest('facebook')[0], 'फेसबुक');
});

test('converts romanized sentences, digits and sentence punctuation', () => {
  assert.equal(smart.toDevanagari('mero desh nepal ho.'), 'मेरो देश नेपाल हो।');
  assert.equal(smart.toDevanagari('NEPSE aaja 20 ankale badhyo'), 'NEPSE आज २० अंकले बढ्यो');
  assert.equal(smart.toDevanagari('2083', { digits: false }), '2083');
});

test('custom lexicons and learned choices stay local to the typer instance', () => {
  const lexicon = smart.buildLexicon(['बालेन शाहले भने। बालेन शाह काठमाडौंका मेयर हुन्।']);
  assert.equal(lexicon['बालेन'], 2);
  const typer = smart.createTyper({ words: lexicon });
  assert.equal(typer.suggest('balen')[0], 'बालेन');
  typer.learn('pani', 'पानी');
  assert.equal(typer.suggest('pani')[0], 'पानी');
  const restored = smart.createTyper({ learned: typer.exportLearned() });
  assert.equal(restored.suggest('pani')[0], 'पानी');
});

test('the lexicon exposes a stable package descriptor and useful size', () => {
  assert.equal(smart.describe().name, '@lacspace/nepali-typing');
  assert.ok(smart.createTyper().size() > 100);
});
