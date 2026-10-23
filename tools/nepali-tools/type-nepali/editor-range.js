(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.NepaliTypingRange = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  // A token excludes whitespace, protected-text braces, and common punctuation.
  // The range always describes the complete token, not just the prefix before the caret.
  const TOKEN_CHAR = /[^\s{}.,!?;:।…()\[\]"'“”‘’]/u;

  function getCurrentWord(value, pos) {
    if (typeof value !== 'string' || !Number.isInteger(pos)) return null;
    const caret = Math.max(0, Math.min(pos, value.length));
    if (caret < value.length && /\s/.test(value[caret])) return null;
    let start = caret;
    let end = caret;

    while (start > 0 && TOKEN_CHAR.test(value[start - 1])) start--;
    while (end < value.length && TOKEN_CHAR.test(value[end])) end++;

    if (start === end) return null;
    const word = value.slice(start, end);
    return { word, start, end, pos: caret };
  }

  return { getCurrentWord };
});
