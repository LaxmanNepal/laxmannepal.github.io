/*
 * Daraz affiliate link helper for LaxmanNepal.
 *
 * This module deliberately does not guess Daraz tracking parameters. Daraz's
 * current affiliate agreement says affiliates must use hyperlinks supplied by
 * Daraz and that tracking is handled by Daraz. Configure the exact approved
 * hyperlink template in /data/daraz-affiliate.json after approval.
 */
(function (window, document) {
  'use strict';

  function build(template, destination, product) {
    if (!template || !destination) return null;
    return template
      .replaceAll('{url}', encodeURIComponent(destination))
      .replaceAll('{product}', encodeURIComponent(product || ''));
  }

  function isConfigured(config) {
    return !!(config && config.enabled && config.tracking_template &&
      !config.tracking_template.includes('PASTE_YOUR_DARAZ'));
  }

  function decorate(root, config) {
    if (!isConfigured(config)) return 0;
    let count = 0;
    (root || document).querySelectorAll('[data-daraz-url]').forEach(function (el) {
      const destination = el.getAttribute('data-daraz-url');
      const product = el.getAttribute('data-daraz-product') || '';
      const href = build(config.tracking_template, destination, product);
      if (!href) return;
      el.href = href;
      el.target = '_blank';
      el.rel = 'sponsored nofollow noopener';
      el.dataset.affiliateReady = 'true';
      count += 1;
    });
    return count;
  }

  window.LaxmanDarazAffiliate = {
    build: build,
    decorate: decorate,
    configured: isConfigured
  };

  fetch('/data/daraz-affiliate.json', { cache: 'no-store' })
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (config) {
      if (!config) return;
      window.LaxmanDarazAffiliate.config = config;
      decorate(document, config);
      document.dispatchEvent(new CustomEvent('laxman-daraz-affiliate-ready', {
        detail: { configured: isConfigured(config) }
      }));
    })
    .catch(function () {});
})(window, document);
