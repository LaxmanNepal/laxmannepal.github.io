(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.NepaliTypingMetrics = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';
  function graphemes(value) {
    const text = String(value ?? '');
    if (typeof Intl !== 'undefined' && Intl.Segmenter) {
      return Array.from(new Intl.Segmenter('ne', { granularity: 'grapheme' }).segment(text), part => part.segment);
    }
    return Array.from(text);
  }
  function calculateMetrics(targetText, typedText, elapsedMs = 0) {
    const target = graphemes(targetText);
    const typed = graphemes(typedText);
    let correct = 0, mismatches = 0;
    for (let i = 0; i < Math.min(target.length, typed.length); i++) {
      if (target[i] === typed[i]) correct++;
      else mismatches++;
    }
    const extra = Math.max(0, typed.length - target.length);
    const remaining = Math.max(0, target.length - typed.length);
    const minutes = Math.max(0, Number(elapsedMs) || 0) / 60000;
    const accuracy = typed.length ? Math.round((correct / typed.length) * 1000) / 10 : 0;
    const wpm = minutes > 0 ? Math.round((correct / 5 / minutes) * 10) / 10 : 0;
    const cpm = minutes > 0 ? Math.round((correct / minutes) * 10) / 10 : 0;
    return { targetCharacters: target.length, typedCharacters: typed.length, correctCharacters: correct, errors: mismatches + extra, remaining, accuracy, wpm, cpm, elapsedMs: Math.max(0, Number(elapsedMs) || 0) };
  }
  return { graphemes, calculateMetrics };
});
