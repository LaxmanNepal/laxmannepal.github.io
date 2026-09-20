(() => {
  "use strict";
  const BASE = "https://raw.githubusercontent.com/LaxmanNepal/Drumkit/main/";
  const sounds = {
    w: BASE + "sounds/crash.mp3", a: BASE + "sounds/kick-bass.mp3", s: BASE + "sounds/snare.mp3",
    d: BASE + "sounds/tom-1.mp3", j: BASE + "sounds/tom-2.mp3", k: BASE + "sounds/tom-3.mp3", l: BASE + "sounds/tom-4.mp3"
  };
  const buttons = [...document.querySelectorAll(".drum")];
  const statusText = document.getElementById("statusText");
  const audioCache = new Map();
  const activeTimers = new Map();
  function getAudio(key) {
    if (!sounds[key]) return null;
    if (!audioCache.has(key)) { const audio = new Audio(sounds[key]); audio.preload = "auto"; audioCache.set(key, audio); }
    return audioCache.get(key);
  }
  function animate(key) {
    const button = document.querySelector(`.drum[data-key="${key}"]`);
    if (!button) return;
    button.classList.remove("pressed"); void button.offsetWidth; button.classList.add("pressed");
    clearTimeout(activeTimers.get(key));
    activeTimers.set(key, setTimeout(() => button.classList.remove("pressed"), 110));
  }
  function playSound(key) {
    const normalized = String(key).toLowerCase(), audio = getAudio(normalized);
    if (!audio) return;
    audio.currentTime = 0;
    const result = audio.play();
    if (result?.catch) result.catch(() => { statusText.textContent = "Tap a drum once to enable sound"; });
    animate(normalized);
    statusText.textContent = `Playing: ${normalized.toUpperCase()}`;
  }
  buttons.forEach(button => {
    const key = button.dataset.key;
    button.addEventListener("pointerdown", event => { event.preventDefault(); playSound(key); });
    button.addEventListener("keydown", event => {
      if (event.key === " " || event.key === "Enter") { event.preventDefault(); playSound(key); }
    });
  });
  document.addEventListener("keydown", event => {
    if (event.repeat || event.ctrlKey || event.metaKey || event.altKey) return;
    playSound(event.key);
  });
  const preload = () => Object.keys(sounds).forEach(getAudio);
  if ("requestIdleCallback" in window) window.requestIdleCallback(preload); else window.setTimeout(preload, 500);
})();