(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>\"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));
  const fmt = value => {
    const n = Number(value ?? 0);
    return Number.isFinite(n)
      ? new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
      : '—';
  };
  const dateFmt = value => {
    if (!value) return '—';
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(date);
  };

  function injectStyles() {
    if ($('#lnEnhancementStyles')) return;
    const style = document.createElement('style');
    style.id = 'lnEnhancementStyles';
    style.textContent = `
      .lnAppsMeta{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:0 0 14px;color:var(--ink)}
      .lnAppsStatus{font-size:.72rem;color:var(--muted)}
      .lnAppCard{position:relative;display:flex;flex-direction:column;min-height:225px;padding:22px;border-radius:24px;overflow:hidden;cursor:pointer;text-decoration:none!important;color:inherit;background:var(--glass);border:1px solid var(--border);backdrop-filter:blur(24px) saturate(180%);-webkit-backdrop-filter:blur(24px) saturate(180%);box-shadow:var(--shadow);transition:transform .35s var(--ease),box-shadow .35s}
      .lnAppCard:hover{transform:translateY(-8px);box-shadow:0 30px 75px rgba(31,38,50,.16)}
      .lnAppCard:focus-visible{outline:3px solid rgba(22,119,255,.35);outline-offset:3px}
      .lnAppIcon{width:52px;height:52px;display:grid;place-items:center;border-radius:16px;font-size:25px;background:rgba(22,119,255,.09);border:1px solid var(--border);margin-bottom:16px}
      .lnAppCard h3{margin:0 0 7px;font:700 1.05rem Poppins,Inter,sans-serif}
      .lnAppCard p{margin:0 0 16px;color:var(--muted);font-size:.82rem;line-height:1.6;flex:1}
      .lnAppFoot{display:flex;justify-content:space-between;gap:8px;font-size:.7rem;color:var(--muted)}
      .lnAppOpen{color:var(--blue);font-weight:800}
      .lnAppSearch{width:280px;max-width:100%;padding:12px 15px;border:1px solid var(--border);outline:0;border-radius:14px;background:var(--glass);color:var(--ink)}
      .lnAppFilters{display:flex;gap:6px;flex-wrap:wrap}
      .lnAppFilter{border:1px solid var(--border);background:var(--glass);color:var(--muted);padding:9px 12px;border-radius:12px;cursor:pointer;font-size:.75rem}
      .lnAppFilter.active{background:#101828;color:#fff}
      .lnAppsError{grid-column:1/-1;padding:24px;border-radius:20px;border:1px dashed #98a2b3;color:var(--muted);text-align:center}
      .ytHero{margin-top:18px;padding:20px;border-radius:28px;overflow:hidden;position:relative}
      .ytHero:before{content:"";position:absolute;inset:-50%;background:conic-gradient(from 90deg,#ff0033,#7c3aed,#06b6d4,#22c55e,#ff0033);opacity:.12;animation:ytspin 14s linear infinite}
      .ytIdentity{position:relative;display:flex;align-items:center;gap:16px}.ytIdentity h3{margin:0;font-size:20px}.ytIdentity p{margin:3px 0;color:var(--muted)}.ytAvatar{width:64px;height:64px;border-radius:50%;object-fit:cover;border:3px solid rgba(255,255,255,.8)}.ytIdentity .btn{margin-left:auto}
      .ytStats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:14px}.ytStat{padding:18px;border-radius:22px;display:grid;grid-template-columns:auto 1fr;column-gap:10px;align-items:center;transition:transform .35s,box-shadow .35s}.ytStat:hover{transform:translateY(-6px);box-shadow:0 18px 50px rgba(15,23,42,.12)}.ytStat b{font-size:27px}.ytStat small{grid-column:2;color:var(--muted)}.ytIcon{grid-row:span 2;width:34px;height:34px;border-radius:12px;display:grid;place-items:center;font-weight:900}.ytRed{background:#fee2e2;color:#ef4444}.ytBlue{background:#dbeafe;color:#2563eb}.ytPurple{background:#ede9fe;color:#7c3aed}.ytGreen{background:#dcfce7;color:#16a34a}
      .ytGrid{display:grid;grid-template-columns:1.5fr 1fr;gap:14px;margin-top:14px}.ytChart,.ytBreakdown{padding:18px;border-radius:24px;min-height:150px}.ytSpark{width:100%;height:90px;color:#ef4444;margin-top:18px;overflow:visible}.chartLabels{display:flex;justify-content:space-between;color:var(--muted);font-size:12px}.mix{display:flex;gap:34px;margin:18px 0}.mix b{display:block;font-size:30px}.mix span{color:var(--muted);font-size:13px}.bar{height:10px;border-radius:99px;background:#e2e8f0;overflow:hidden}.bar i{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#ef4444,#7c3aed,#06b6d4);animation:ytbar 1.2s ease-out}
      .youtubeDataPanel{margin-top:14px;padding:18px;border-radius:26px}.panelTitle{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px}.panelTitle span{font-size:12px;color:var(--muted)}.ytVideos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.ytVideo{display:block;width:100%;padding:0;text-align:left;color:inherit;text-decoration:none;border-radius:20px;overflow:hidden;background:rgba(255,255,255,.72);border:1px solid rgba(148,163,184,.18);cursor:pointer;transition:transform .35s,box-shadow .35s}.ytVideo:hover{transform:translateY(-7px) scale(1.01);box-shadow:0 20px 55px rgba(15,23,42,.14)}.ytThumbWrap{position:relative;aspect-ratio:16/9;background:#e2e8f0;overflow:hidden}.ytThumb{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s}.ytVideo:hover .ytThumb{transform:scale(1.05)}.ytPlay{position:absolute;left:12px;bottom:12px;width:36px;height:36px;border-radius:12px;background:rgba(255,0,51,.92);color:white;display:grid;place-items:center;font-size:13px}.ytVideoBody{padding:12px}.ytVideoBody b{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:14px;line-height:1.4}.ytVideoBody span{display:block;margin-top:7px;color:var(--muted);font-size:12px}.ytLatest{margin-top:28px}.ytMoreWrap{text-align:center}.ytMore{display:inline-flex;margin:18px auto 0;padding:12px 18px;border-radius:999px;background:#111827;color:#fff;text-decoration:none;font-weight:700}.ytFoot{margin-top:18px;padding-top:14px;border-top:1px solid rgba(148,163,184,.2);color:var(--muted);font-size:12px}
      #ytVideoModal{position:fixed;inset:0;z-index:99999;display:grid;place-items:center;visibility:hidden;opacity:0;transition:opacity .22s,visibility .22s;padding:20px}.ytModalBackdrop{position:fixed;inset:0;background:rgba(2,6,23,.72);backdrop-filter:blur(16px)}#ytVideoModal.open{visibility:visible;opacity:1}.ytModalBox{position:relative;width:min(960px,100%);background:rgba(255,255,255,.96);border-radius:26px;overflow:hidden;box-shadow:0 30px 100px rgba(0,0,0,.35);transform:translateY(20px) scale(.96);transition:transform .28s}.open .ytModalBox{transform:none}.ytModalPlayer{aspect-ratio:16/9;background:#000}.ytModalPlayer iframe{width:100%;height:100%;border:0}.ytModalClose{position:absolute;right:14px;top:14px;width:42px;height:42px;border:0;border-radius:50%;background:rgba(255,255,255,.95);font-size:28px;cursor:pointer;z-index:2}.ytModalInfo{padding:15px 18px;display:flex;justify-content:space-between;gap:15px}.ytModalInfo span{color:var(--muted);font-size:13px}.ytModalOpen{overflow:hidden}
      @keyframes ytspin{to{transform:rotate(360deg)}}@keyframes ytbar{from{width:0}}
      @media(max-width:800px){.ytStats{grid-template-columns:repeat(2,1fr)}.ytGrid{grid-template-columns:1fr}.ytVideos{grid-template-columns:repeat(2,minmax(0,1fr))}}
      @media(max-width:560px){.lnAppSearch{width:100%}.ytIdentity{align-items:flex-start;flex-wrap:wrap}.ytIdentity .btn{margin-left:0;width:100%;text-align:center}.ytStats{gap:9px}.ytStat{padding:14px;border-radius:18px}.ytStat b{font-size:22px}.ytIcon{width:30px;height:30px}.ytVideos{grid-template-columns:1fr}.ytHero,.youtubeDataPanel,.ytChart,.ytBreakdown{border-radius:20px;padding:14px}.ytAvatar{width:54px;height:54px}.ytModalInfo{display:block}.ytModalInfo span{display:block;margin-top:6px}}
      @media(prefers-reduced-motion:reduce){.ytHero:before,.bar i{animation:none}.ytStat,.ytVideo,.ytThumb,#ytVideoModal,.ytModalBox,.lnAppCard{transition:none}}
    `;
    document.head.appendChild(style);
  }

  let apps = [];
  let selectedCategory = 'All';

  async function loadApps() {
    const section = $('#apps');
    const host = section?.querySelector('.apps');
    if (!section || !host) return;
    try {
      const response = await fetch(`/data/apps.json?v=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      apps = Array.isArray(data.apps) ? data.apps.filter(app => app.status === 'online') : [];
    } catch (error) {
      console.error('[Laxman Nepal] Apps data failed', error);
      apps = [];
    }
    setupApps(section, host);
  }

  function setupApps(section, host) {
    const oldToolbar = section.querySelector('.appsToolbar');
    if (oldToolbar) oldToolbar.remove();
    const toolbar = document.createElement('div');
    toolbar.className = 'appsToolbar';
    toolbar.innerHTML = '<div class="lnAppFilters"></div><input class="lnAppSearch" type="search" placeholder="Search apps…" aria-label="Search apps">';
    const header = host.parentNode;
    header.insertBefore(toolbar, host);

    const meta = document.createElement('div');
    meta.className = 'lnAppsMeta';
    meta.innerHTML = `<strong>Available apps</strong><span class="lnAppsStatus">${apps.length} online</span>`;
    header.insertBefore(meta, host);

    const filters = $('.lnAppFilters', toolbar);
    const search = $('.lnAppSearch', toolbar);
    const categories = ['All', ...new Set(apps.map(app => app.category).filter(Boolean))];
    filters.innerHTML = categories.map(category => `<button class="lnAppFilter${category === 'All' ? ' active' : ''}" type="button">${esc(category)}</button>`).join('');
    filters.querySelectorAll('button').forEach(button => {
      button.addEventListener('click', () => {
        selectedCategory = button.textContent;
        filters.querySelectorAll('button').forEach(item => item.classList.toggle('active', item === button));
        renderApps(host, search.value);
      });
    });
    search.addEventListener('input', () => renderApps(host, search.value));
    renderApps(host, '');
  }

  function renderApps(host, query) {
    const term = String(query || '').toLowerCase().trim();
    const visible = apps.filter(app => {
      const categoryMatch = selectedCategory === 'All' || app.category === selectedCategory;
      const text = [app.name, app.description, app.category, ...(app.keywords || [])].join(' ').toLowerCase();
      return categoryMatch && (!term || text.includes(term));
    });
    host.innerHTML = visible.length
      ? visible.map(app => `<a class="lnAppCard" href="${esc(app.url)}" data-app-id="${esc(app.id)}"><div class="lnAppIcon" aria-hidden="true">${esc(app.icon || '◉')}</div><h3>${esc(app.name)}</h3><p>${esc(app.description || 'Explore this app by Laxman Nepal.')}</p><div class="lnAppFoot"><span>${esc(app.category || 'App')}</span><span class="lnAppOpen">Open App ↗</span></div></a>`).join('')
      : '<div class="lnAppsError">No online apps match your search.</div>';
    host.querySelectorAll('.lnAppCard').forEach(card => card.addEventListener('click', () => {
      try {
        const id = card.dataset.appId;
        const recent = [id, ...JSON.parse(localStorage.getItem('ln:recentApps') || '[]').filter(item => item !== id)].slice(0, 8);
        localStorage.setItem('ln:recentApps', JSON.stringify(recent));
      } catch {}
    }));
  }

  function videoArray(data, keys) {
    for (const key of keys) if (Array.isArray(data[key]) && data[key].length) return data[key];
    return [];
  }
  const videoId = video => video?.id || video?.videoId || '';
  const isShort = video => video?.isShort === true || video?.type === 'short' || video?.format === 'short' || (Number(video?.durationSeconds ?? video?.duration_seconds ?? 0) > 0 && Number(video?.durationSeconds ?? video?.duration_seconds ?? 0) <= 60);

  function spark(values) {
    const nums = values.map(Number).filter(Number.isFinite);
    if (nums.length < 2) return '<div class="chartLabels"><span>Dataset activity</span><span>Not enough points</span></div>';
    const max = Math.max(...nums), min = Math.min(...nums), width = 320, height = 90;
    const points = nums.map((value, index) => `${index / (nums.length - 1) * width},${height - (value - min) / (max - min || 1) * height}`).join(' ');
    return `<svg class="ytSpark" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="Dataset activity visualization"><polyline points="${points}" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round"/></svg>`;
  }

  function openVideo(video) {
    const id = videoId(video);
    if (!id) return;
    let modal = $('#ytVideoModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'ytVideoModal';
      modal.innerHTML = '<div class="ytModalBackdrop"></div><div class="ytModalBox" role="dialog" aria-modal="true"><button class="ytModalClose" aria-label="Close video">×</button><div class="ytModalPlayer"></div><div class="ytModalInfo"></div></div>';
      document.body.appendChild(modal);
      $('.ytModalBackdrop', modal).addEventListener('click', closeVideo);
      $('.ytModalClose', modal).addEventListener('click', closeVideo);
    }
    const title = video.title || video.snippet?.title || 'YouTube video';
    $('.ytModalPlayer', modal).innerHTML = `<iframe src="https://www.youtube.com/embed/${encodeURIComponent(id)}?autoplay=1&rel=0&modestbranding=1" title="${esc(title)}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`;
    $('.ytModalInfo', modal).innerHTML = `<b>${esc(title)}</b><span>${fmt(video.views ?? video.statistics?.viewCount)} views · ${fmt(video.likes ?? video.statistics?.likeCount)} likes · ${fmt(video.comments ?? video.statistics?.commentCount)} comments</span>`;
    modal.classList.add('open');
    document.body.classList.add('ytModalOpen');
  }

  function closeVideo() {
    const modal = $('#ytVideoModal');
    if (!modal) return;
    modal.classList.remove('open');
    document.body.classList.remove('ytModalOpen');
    setTimeout(() => { const player = $('.ytModalPlayer', modal); if (player) player.innerHTML = ''; }, 220);
  }

  function videoCard(video) {
    const title = video.title || video.snippet?.title || 'Untitled video';
    const thumb = video.thumbnail || video.thumbnails?.high?.url || video.thumbnails?.medium?.url || video.snippet?.thumbnails?.high?.url || '';
    return `<button class="ytVideo" type="button" data-video-id="${esc(videoId(video))}"><div class="ytThumbWrap"><img class="ytThumb" loading="lazy" src="${esc(thumb)}" alt="${esc(title)}"><span class="ytPlay">▶</span></div><div class="ytVideoBody"><b>${esc(title)}</b><span>${fmt(video.views ?? video.statistics?.viewCount)} views · ${fmt(video.likes ?? video.statistics?.likeCount)} likes · ${fmt(video.comments ?? video.statistics?.commentCount)} comments</span></div></button>`;
  }

  async function loadYouTube() {
    const section = $('#youtube');
    if (!section) return;
    try {
      const response = await fetch(`/data/youtube.json?v=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (!data.channel?.statistics) throw new Error('Invalid YouTube dataset');
      renderYouTube(section, data);
    } catch (error) {
      console.error('[Laxman Nepal] YouTube data failed', error);
    }
  }

  function renderYouTube(section, data) {
    const channel = data.channel || {};
    const stats = channel.statistics || data.statistics || {};
    const analysis = data.analysis || {};
    const popular = videoArray(data, ['popularVideos', 'topVideos', 'videos']).filter(video => !isShort(video)).sort((a, b) => Number(b.views ?? b.statistics?.viewCount ?? 0) - Number(a.views ?? a.statistics?.viewCount ?? 0));
    const recent = videoArray(data, ['recentVideos', 'latestVideos', 'latestUploads', 'recentUploads']);
    const analyzed = Number(analysis.videosFetched || 0);
    const shorts = Number(analysis.shortsCount || 0);
    const longForm = Number(analysis.longFormCount || 0);
    const channelTitle = channel.title || data.channelTitle || 'Laxman Nepal';

    section.innerHTML = `<div class="wrap"><div class="sectionHead reveal in"><div><div class="kicker">YouTube · @laxmannepalofficial</div><h2 class="title">Laxman Nepal on YouTube.</h2></div><div class="desc">Public channel data from the cached YouTube Data API dataset.</div></div><div class="ytHero glass"><div class="ytIdentity"><img src="${esc(channel.thumbnail || '')}" alt="${esc(channelTitle)}" class="ytAvatar"><div><h3>${esc(channelTitle)}</h3><p>@laxmannepalofficial</p></div><a class="btn" href="/youtube/">Open YouTube dashboard ↗</a></div></div><div class="ytStats"><div class="ytStat glass"><span class="ytIcon ytRed">●</span><b>${fmt(stats.subscriberCount)}</b><small>Subscribers</small></div><div class="ytStat glass"><span class="ytIcon ytBlue">◉</span><b>${fmt(stats.viewCount)}</b><small>Total views</small></div><div class="ytStat glass"><span class="ytIcon ytPurple">▶</span><b>${fmt(stats.videoCount)}</b><small>Total videos</small></div><div class="ytStat glass"><span class="ytIcon ytGreen">↗</span><b>${fmt(analyzed)}</b><small>Videos analyzed</small></div></div><div class="ytGrid"><div class="ytChart glass"><div class="panelTitle"><strong>Dataset activity</strong><span>Collected public data</span></div>${spark([analysis.totalViewsFetched || 0, analysis.totalLikesFetched || 0, analysis.totalCommentsFetched || 0])}<div class="chartLabels"><span>${fmt(analysis.totalViewsFetched)} views</span><span>${fmt(analysis.totalLikesFetched)} likes</span><span>${fmt(analysis.totalCommentsFetched)} comments</span></div></div><div class="ytBreakdown glass"><div class="panelTitle"><strong>Content mix</strong><span>${fmt(analyzed)} analyzed</span></div><div class="mix"><div><b>${fmt(shorts)}</b><span>Shorts</span></div><div><b>${fmt(longForm)}</b><span>Long-form</span></div></div><div class="bar"><i style="width:${analyzed ? Math.min(100, shorts / analyzed * 100) : 0}%"></i></div></div></div><div class="youtubeDataPanel glass"><div class="panelTitle"><strong>Popular long-form videos</strong><span>Top ${Math.min(popular.length, 10)}</span></div><div class="ytVideos">${popular.slice(0, 10).map(videoCard).join('') || '<div class="lnAppsError">No long-form video data available yet.</div>'}</div><div class="ytMoreWrap"><a class="ytMore" href="/youtube/">More popular videos →</a></div>${recent.length ? `<div class="ytLatest"><div class="panelTitle"><strong>Latest uploads</strong><span>${Math.min(recent.length, 6)} shown</span></div><div class="ytVideos">${recent.slice(0, 6).map(videoCard).join('')}</div></div>` : ''}<div class="ytFoot">Last sync: ${dateFmt(data.lastUpdated || data.updatedAt)} · ${esc(data.dataSource || 'YouTube Data API v3')}</div></div></div>`;
    section.querySelectorAll('.ytVideo').forEach(button => button.addEventListener('click', () => {
      const video = [...popular, ...recent].find(item => videoId(item) === button.dataset.videoId);
      if (video) openVideo(video);
    }));
  }

  function init() {
    injectStyles();
    loadApps();
    loadYouTube();
    document.addEventListener('keydown', event => { if (event.key === 'Escape') closeVideo(); }, { passive: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
