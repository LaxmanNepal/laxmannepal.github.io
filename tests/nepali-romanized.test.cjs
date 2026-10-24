const test = require('node:test');
const assert = require('node:assert/strict');
const { transliterate, convertWord } = require('../tools/nepali-tools/type-nepali/engines/romanized.js');

test('common Nepali words use deterministic local exceptions', () => {
  assert.equal(convertWord('namaste'), 'नमस्ते');
  assert.equal(convertWord('mero'), 'मेरो');
  assert.equal(convertWord('nepal'), 'नेपाल');
  assert.equal(convertWord('thapa'), 'थापा');
});

test('aspirated and retroflex tokens preserve the documented case distinction', () => {
  assert.equal(transliterate('th'), 'थ');
  assert.equal(transliterate('Th'), 'ठ');
  assert.equal(transliterate('sh'), 'श');
  assert.equal(transliterate('Sh'), 'ष');
});

test('conjunct tokens are handled as a single token', () => {
  assert.equal(transliterate('ksh'), 'क्ष');
  assert.equal(transliterate('chh'), 'छ');
  assert.equal(transliterate('gy'), 'ज्ञ');
});

test('punctuation, spaces, digits, and non-Latin characters are preserved', () => {
  assert.equal(transliterate('namaste, 123! नेपाली'), 'नमस्ते, 123! नेपाली');
});

test('empty and non-string input do not throw', () => {
  assert.equal(transliterate(''), '');
  assert.equal(transliterate(null), '');
  assert.equal(convertWord(null), '');
});

test('the converter remains deterministic without network access', () => {
  for (let i = 0; i < 3; i++) assert.equal(convertWord('dhanyabad'), 'धन्यवाद');
});
