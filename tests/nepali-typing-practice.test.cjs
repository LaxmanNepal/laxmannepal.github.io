const test = require('node:test');
const assert = require('node:assert/strict');
const { graphemes, calculateMetrics } = require('../tools/nepali-tools/nepali-typing-practice/metrics.js');

test('counts Devanagari grapheme clusters rather than raw UTF-16 units', () => {
  assert.equal(graphemes('कि').length, 1);
  assert.equal(graphemes('नेपाली').length, 3);
});

test('calculates correct characters, errors, remaining, and accuracy', () => {
  const result = calculateMetrics('नेपाल', 'नेपल', 60000);
  assert.equal(result.targetCharacters, 3);
  assert.equal(result.typedCharacters, 3);
  assert.equal(result.correctCharacters, 2);
  assert.equal(result.errors, 1);
  assert.equal(result.remaining, 0);
  assert.equal(result.accuracy, 66.7);
});

test('uses the standard five-characters-per-word WPM formula', () => {
  const result = calculateMetrics('abcdefghij', 'abcdefghij', 60000);
  assert.equal(result.wpm, 2);
  assert.equal(result.cpm, 10);
});

test('handles empty input and extra characters', () => {
  assert.equal(calculateMetrics('नमस्ते', '', 1000).accuracy, 0);
  const result = calculateMetrics('abc', 'abcd', 30000);
  assert.equal(result.errors, 1);
  assert.equal(result.remaining, 0);
});

test('does not return negative time or speed for invalid elapsed input', () => {
  const result = calculateMetrics('abc', 'abc', -100);
  assert.equal(result.elapsedMs, 0);
  assert.equal(result.wpm, 0);
});
