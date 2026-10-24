(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const source = $('#source-text'), result = $('#result-text'), direction = $('#direction'), status = $('#conversion-status');
  function render() {
    const value = source.value;
    if (!value) { result.value = ''; status.textContent = 'Paste text to preview the conversion.'; return; }
    if (direction.value === 'preeti-to-unicode') {
      result.value = window.NepaliPreetiConverter.preetiToUnicode(value);
      status.textContent = window.NepaliPreetiConverter.looksLikePreeti(value)
        ? 'Likely Preeti text · review the converted preview before using it.'
        : 'Input may not be Preeti-encoded. This direction converts all characters; review carefully.';
    } else {
      result.value = window.NepaliPreetiConverter.unicodeToPreeti(value);
      status.textContent = 'Unicode converted to Preeti encoding · apply the Preeti font in your target document to display it.';
    }
  }
  async function copyResult() {
    try { await navigator.clipboard.writeText(result.value); status.textContent = 'Converted text copied.'; }
    catch (_) { result.focus(); result.select(); const ok = document.execCommand('copy'); status.textContent = ok ? 'Converted text copied.' : 'Copy unavailable · select and copy the result manually.'; }
  }
  function downloadResult() {
    const blob = new Blob(['\ufeff', result.value], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = direction.value === 'preeti-to-unicode' ? 'nepali-unicode.txt' : 'nepali-preeti.txt';
    document.body.append(link); link.click(); link.remove(); URL.revokeObjectURL(url);
    status.textContent = 'Converted text downloaded.';
  }
  source.addEventListener('input', render);
  direction.addEventListener('change', render);
  $('#sample').addEventListener('click', () => {
    direction.value = 'preeti-to-unicode';
    source.value = "g]kfn ;/sf/sf k|wfgdGqLn] cfly{s ;'wf/sf] 3f]if0ff ug'{eof] .";
    render();
  });
  $('#copy-result').addEventListener('click', copyResult);
  $('#download-result').addEventListener('click', downloadResult);
  $('#clear-text').addEventListener('click', () => { source.value = ''; result.value = ''; render(); source.focus(); });
  render();
})();
