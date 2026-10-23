// Regression tests for caret-safe candidate ranges.
// Run with: node --test tests/nepali-typing-range.test.cjs
// The mid-token case documents the current defect: the old UI captured the
// prefix before the caret as "word" while the range covered the entire token.
const test = require('node:test');
const assert = require('node:assert/strict');
const { getCurrentWord } = require('../tools/nepali-tools/type-nepali/editor-range.js');

test('captures the complete token when the caret is inside it', () => {
  const value = 'hello namaste world';
  const range = getCurrentWord(value, 10); // hello nama|ste world
  assert.deepEqual(range, { word: 'namaste', start: 6, end: 13, pos: 10 });
  assert.equal(value.slice(range.start, range.end), range.word);
});

test('captures the token at its end', () => {
  const value = 'namaste';
  assert.deepEqual(getCurrentWord(value, value.length), {
    word: 'namaste', start: 0, end: 7, pos: 7
  });
});

test('handles punctuation without including it in the token', () => {
  const value = 'namaste, Nepal';
  assert.deepEqual(getCurrentWord(value, 7), {
    word: 'namaste', start: 0, end: 7, pos: 7
  });
});

test('does not treat brace-protected English as an unfinished token', () => {
  const value = 'hello {world} namaste';
  assert.deepEqual(getCurrentWord(value, 9), {
    word: 'world', start: 7, end: 12, pos: 9
  });
});

test('returns null when the caret is at whitespace or has no token before it', () => {
  assert.equal(getCurrentWord('hello world', 6), null);
  assert.equal(getCurrentWord(' hello', 0), null);
});
