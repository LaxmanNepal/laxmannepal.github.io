(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const target = $('#target-text'), input = $('#practice-input'), duration = $('#duration');
  const passageSelect = $('#sample-passage'), startButton = $('#start'), pauseButton = $('#pause'), resetButton = $('#reset');
  const passages = {
    basic: 'नेपाल सुन्दर देश हो। नेपाली भाषा हाम्रो पहिचान हो।',
    paragraph: 'नेपाल हिमाल, पहाड र तराई भएको सुन्दर देश हो। यहाँ धेरै भाषा, संस्कृति र परम्परा छन्। नेपाली भाषा हाम्रो साझा सम्पर्कको भाषा हो।',
    mixed: 'नेपालको राजधानी काठमाडौं हो। २०८३ सालमा नयाँ लक्ष्य बनाऔँ! Typing practice: 12345।',
    custom: ''
  };
  let running = false, startedAt = 0, elapsedBeforePause = 0, interval = null, elapsedMs = 0;
  const pad = n => String(n).padStart(2, '0');
  function formatTime(ms) { const seconds = Math.floor(ms / 1000); return pad(Math.floor(seconds / 60)) + ':' + pad(seconds % 60); }
  function currentElapsed() { return elapsedBeforePause + (running ? Date.now() - startedAt : 0); }
  function setStatus(message) { $('#practice-status').textContent = message; }
  function updateMetrics() {
    elapsedMs = currentElapsed();
    const result = window.NepaliTypingMetrics.calculateMetrics(target.value, input.value, elapsedMs);
    $('#wpm').textContent = result.wpm;
    $('#cpm').textContent = result.cpm;
    $('#accuracy').textContent = result.accuracy + '%';
    $('#errors').textContent = result.errors;
    $('#remaining').textContent = result.remaining;
    $('#correct').textContent = result.correctCharacters;
    $('#timer').textContent = formatTime(elapsedMs);
    $('#timer-mode').textContent = Number(duration.value) ? duration.value + '-minute session' : 'Untimed session';
  }
  function stopTimer(message) {
    if (running) elapsedBeforePause += Date.now() - startedAt;
    running = false; startedAt = 0;
    if (interval) clearInterval(interval);
    interval = null;
    startButton.disabled = false;
    pauseButton.disabled = true;
    if (message) setStatus(message);
    updateMetrics();
  }
  function tick() {
    elapsedMs = currentElapsed();
    const limit = Number(duration.value) * 60000;
    if (limit > 0 && elapsedMs >= limit) {
      elapsedBeforePause = limit;
      stopTimer('Time finished · review your result or reset to try again');
      startButton.disabled = true;
      return;
    }
    updateMetrics();
  }
  function resetPractice(message = 'Ready when you are') {
    if (interval) clearInterval(interval);
    interval = null; running = false; startedAt = 0; elapsedBeforePause = 0; elapsedMs = 0;
    input.value = '';
    startButton.disabled = false; pauseButton.disabled = true;
    setStatus(message); updateMetrics();
  }
  startButton.addEventListener('click', () => {
    if (running || startButton.disabled) return;
    running = true; startedAt = Date.now();
    startButton.disabled = true; pauseButton.disabled = false;
    setStatus('Practice running · type the passage below');
    interval = setInterval(tick, 200);
    input.focus(); updateMetrics();
  });
  pauseButton.addEventListener('click', () => {
    if (!running) return;
    stopTimer('Paused · press Start practice to resume');
  });
  resetButton.addEventListener('click', () => resetPractice());
  input.addEventListener('input', () => {
    updateMetrics();
    const result = window.NepaliTypingMetrics.calculateMetrics(target.value, input.value, currentElapsed());
    if (target.value && input.value === target.value) {
      stopTimer('Passage completed · well done!');
      startButton.disabled = true;
    }
  });
  target.addEventListener('input', () => resetPractice('Passage changed · ready for a new attempt'));
  passageSelect.addEventListener('change', () => {
    target.value = passages[passageSelect.value] || '';
    resetPractice(passageSelect.value === 'custom' ? 'Enter your own passage, then start' : 'Passage changed · ready for a new attempt');
  });
  duration.addEventListener('change', () => resetPractice('Time limit changed · ready for a new attempt'));
  updateMetrics();
})();
