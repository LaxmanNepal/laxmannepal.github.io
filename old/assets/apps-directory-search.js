(() => {
  'use strict';
  const grid = document.querySelector('.grid');
  if (!grid) return;
  const cards = [...grid.querySelectorAll('.card')];
  if (!cards.length || document.getElementById('lnAppsSearch')) return;

  const style = document.createElement('style');
  style.textContent = '.lnAppsToolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:25px 0}.lnAppsSearch{flex:1;min-width:240px;padding:13px 15px;border:1px solid #d0d5dd;border-radius:14px;background:#fff;color:#101828;font:inherit;outline:none}.lnAppsSearch:focus{border-color:#1677ff;box-shadow:0 0 0 3px #1677ff22}.lnAppsCount{font-size:.82rem;color:#667085}.lnAppsEmpty{grid-column:1/-1;padding:30px;text-align:center;border:1px dashed #98a2b3;border-radius:18px;color:#667085}';
  document.head.appendChild(style);

  const toolbar = document.createElement('div');
  toolbar.className = 'lnAppsToolbar';
  toolbar.innerHTML = '<label for="lnAppsSearch" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0">Search apps</label><input id="lnAppsSearch" class="lnAppsSearch" type="search" placeholder="Search apps, tools, finance, media…" autocomplete="off"><span class="lnAppsCount" aria-live="polite"></span>';
  grid.parentNode.insertBefore(toolbar, grid);

  const input = toolbar.querySelector('input');
  const count = toolbar.querySelector('.lnAppsCount');
  const empty = () => {
    grid.querySelector('.lnAppsEmpty')?.remove();
    const node = document.createElement('div');
    node.className = 'lnAppsEmpty';
    node.textContent = `No apps found for “${input.value.trim()}”.`;
    grid.appendChild(node);
  };
  const filter = () => {
    const q = input.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const haystack = `${card.textContent} ${card.getAttribute('data-search') || ''}`.toLowerCase();
      const show = !q || haystack.includes(q);
      card.hidden = !show;
      if (show) visible++;
    });
    count.textContent = `${visible} app${visible === 1 ? '' : 's'} available`;
    if (!visible) empty(); else grid.querySelector('.lnAppsEmpty')?.remove();
  };

  input.value = new URLSearchParams(location.search).get('q') || '';
  input.addEventListener('input', filter);
  filter();
})();
