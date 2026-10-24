(() => {
  'use strict';
  const status = document.querySelector('#network-status');
  const updateButton = document.querySelector('#reload-update');
  const updateNetworkStatus = () => {
    if (!status) return;
    status.textContent = navigator.onLine
      ? 'Online · local typing available'
      : 'Offline · local typing available; online suggestions and voice may not work';
    status.title = navigator.onLine
      ? 'Romanized conversion and drafts are local; Google suggestions and voice may use network services.'
      : 'This page and local conversion are cached. Remote suggestions and browser speech recognition may be unavailable.';
  };
  window.addEventListener('online', updateNetworkStatus);
  window.addEventListener('offline', updateNetworkStatus);
  updateNetworkStatus();

  if (!('serviceWorker' in navigator)) {
    if (status) status.textContent += ' · install/offline cache unsupported';
    return;
  }
  navigator.serviceWorker.register('./sw.js', { scope: './' }).then(registration => {
    const showUpdate = () => {
      if (registration.waiting && navigator.serviceWorker.controller && updateButton) {
        updateButton.hidden = false;
      }
    };
    showUpdate();
    registration.addEventListener('updatefound', () => {
      const worker = registration.installing;
      if (!worker) return;
      worker.addEventListener('statechange', () => {
        if (worker.state === 'installed') showUpdate();
      });
    });
    window.addEventListener('load', () => registration.update().catch(() => {}));
  }).catch(() => {
    if (status) status.textContent += ' · offline cache could not be installed';
  });
  if (updateButton) updateButton.addEventListener('click', () => window.location.reload());
})();
