/*
 * Daraz shopping-link helper for LaxmanNepal.
 *
 * Before affiliate approval, links intentionally go through the site's own
 * /go/daraz/ redirect. When an approved Daraz affiliate template is enabled,
 * the exact Daraz-provided template is used instead.
 */
(function (window, document) {
  'use strict';

  function build(template, destination, product) {
    if (!template || !destination) return null;
    return template
      .replaceAll('{url}', encodeURIComponent(destination))
      .replaceAll('{product}', encodeURIComponent(product || ''));
  }

  function siteRedirect(destination, product) {
    if (!destination) return null;
    return '/go/daraz/?url=' + encodeURIComponent(destination) +
      (product ? '&product=' + encodeURIComponent(product) : '');
  }

  function isConfigured(config) {
    return !!(config && config.enabled && config.tracking_template &&
      !config.tracking_template.includes('PASTE_YOUR_DARAZ'));
  }

  function decorate(root, config) {
    let count = 0;
    (root || document).querySelectorAll('[data-daraz-url]').forEach(function (el) {
      const destination = el.getAttribute('data-daraz-url');
      const product = el.getAttribute('data-daraz-product') || '';
      if (!destination) return;

      const affiliate = isConfigured(config);
      const href = affiliate
        ? build(config.tracking_template, destination, product)
        : siteRedirect(destination, product);
      if (!href) return;

      el.href = href;
      el.target = affiliate ? '_blank' : '_self';
      el.rel = affiliate ? 'sponsored nofollow noopener' : 'nofollow';
      el.dataset.affiliateReady = affiliate ? 'true' : 'false';
      el.dataset.laxmanRedirect = affiliate ? 'false' : 'true';
      count += 1;
    });
    return count;
  }

  window.LaxmanDarazAffiliate = {
    build: build,
    siteRedirect: siteRedirect,
    decorate: decorate,
    configured: isConfigured
  };

  fetch('/data/daraz-affiliate.json', { cache: 'no-store' })
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (config) {
      config = config || {};
      window.LaxmanDarazAffiliate.config = config;
      decorate(document, config);
      document.dispatchEvent(new CustomEvent('laxman-daraz-affiliate-ready', {
        detail: { configured: isConfigured(config) }
      }));
    })
    .catch(function () {
      decorate(document, {});
    });
})(window, document);
