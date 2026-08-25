(() => {
  const DATA_URL = '/data/youtube.json';
  const $ = (s, root = document) => root.querySelector(s);
  const fmt = (n) => {
    const x = Number(n ?? 0);
    return Number.isFinite(x) ? new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(x) : '—';
  };
  const dateFmt = (v) => {
    if (!v) return '—';
    const d = new Date(v);
    return Number.isNaN(d.getTime()) ? '—' : new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(d);
  };
  const escapeHtml = (s) => String(s ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

  function moveYoutubeBeforeApps() {
    const youtube = document.getElementById('youtube');
    const apps = document.getElementById('apps');
    if (youtube && apps && youtube.parentNode === apps.parentNode) apps.parentNode.insertBefore(youtube, apps);
    const links = $('#links');
    if (links) {
      const y = $('a[href="#youtube"]', links);
      const a = $('a[href="#apps"]', links);
      if (y && a) links.insertBefore(y, a);
    }
  }

  function videoArray(data, names) {
    for (const name of names) if (Array.isArray(data[name]) && data[name].length) return data[name];
    return [];
  }

  function videoCard(v) {
    const title = v.title || v.snippet?.title || 'Untitled video';
    const thumb = v.thumbnail || v.thumbnails?.high?.url || v.thumbnails?.medium?.url || v.snippet?.thumbnails?.high?.url || v.snippet?.thumbnails?.medium?.url || '';
    const views = v.views ?? v.statistics?.viewCount ?? 0;
    const likes = v.likes ?? v.statistics?.likeCount ?? 0;
    const comments = v.comments ?? v.statistics?.commentCount ?? 0;
    const url = v.url || (v.id ? `https://www.youtube.com/watch?v=${encodeURIComponent(v.id)}` : '#');
    return `<a class="topVideo" href="${escapeHtml(url)}" target="_blank" rel="noopener"><img class="thumb" loading="lazy" src="${escapeHtml(thumb)}" alt="${escapeHtml(title)}"><div><b>${escapeHtml(title)}</b><span>${fmt(views)} views · ${fmt(likes)} likes · ${fmt(comments)} comments</span></div></a>`;
  }

  function renderYoutube(data) {
    const section = document.getElementById('youtube');
    if (!section || !data) return;
    const channel = data.channel || {};
    const stats = channel.statistics || data.statistics || {};
    const popular = videoArray(data, ['popularVideos', 'topVideos', 'videos']);
    const recent = videoArray(data, ['recentVideos', 'latestVideos', 'latestUploads', 'recentUploads']);
    const combined = [...popular, ...recent.filter(r => !popular.some(p => (p.id || p.videoId) === (r.id || r.videoId)))];
    const channelTitle = channel.title || data.channelTitle || 'Laxman Nepal';
    const channelUrl = channel.url || 'https://www.youtube.com/@laxmannepalofficial';
    const updated = data.lastUpdated || data.updatedAt;
    const top = popular.length ? popular : combined;

    section.innerHTML = `<div class="wrap">
      <div class="sectionHead reveal in">
        <div><div class="kicker">YouTube · @laxmannepalofficial</div><h2 class="title">Laxman Nepal on YouTube.</h2></div>
        <div class="desc">Real public channel data collected by YouTube Data API v3 and cached in this site's JSON. Your API key is never sent to visitors.</div>
      </div>
      <div class="stats reveal in">
        <div class="stat glass"><b>${fmt(stats.subscriberCount)}</b><span>Subscribers</span></div>
        <div class="stat glass"><b>${fmt(stats.viewCount)}</b><span>Total views</span></div>
        <div class="stat glass"><b>${fmt(stats.videoCount)}</b><span>Total videos</span></div>
        <div class="stat glass"><b>${fmt(data.analysis?.videosFetched || combined.length)}</b><span>Videos analyzed</span></div>
      </div>
      <div class="youtubeDataPanel glass reveal in" style="margin-top:16px;padding:18px;border-radius:24px">
        <div style="display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap;margin-bottom:14px">
          <div><strong style="font-family:Poppins">${escapeHtml(channelTitle)}</strong><div class="updated">Last sync: ${dateFmt(updated)} · ${escapeHtml(data.dataSource || 'YouTube Data API v3')}</div></div>
          <a class="btn" href="${escapeHtml(channelUrl)}" target="_blank" rel="noopener">Open channel ↗</a>
        </div>
        <div class="metrics">
          <div class="metric glass"><b>${fmt(data.analysis?.totalViewsFetched)}</b><span>Views in fetched videos</span><small>Average ${fmt(data.analysis?.averageViews)} views/video</small></div>
          <div class="metric glass"><b>${fmt(data.analysis?.totalLikesFetched)}</b><span>Likes in fetched videos</span><small>Average ${fmt(data.analysis?.averageLikes)} likes/video</small></div>
          <div class="metric glass"><b>${fmt(data.analysis?.totalCommentsFetched)}</b><span>Comments in fetched videos</span><small>Average ${fmt(data.analysis?.averageComments)} comments/video</small></div>
          <div class="metric glass"><b>${fmt(data.analysis?.shortsCount)}</b><span>Shorts analyzed</span><small>${fmt(data.analysis?.longFormCount)} long-form videos</small></div>
        </div>
        <div style="margin-top:18px"><div class="panelTitle"><strong>Popular videos</strong><span class="range">Top ${Math.min(top.length, 12)}</span></div><div class="topVideos">${top.slice(0, 12).map(videoCard).join('') || '<div class="empty">No video data available yet.</div>'}</div></div>
        ${recent.length ? `<div style="margin-top:22px"><div class="panelTitle"><strong>Latest uploads</strong><span class="range">${recent.length} available</span></div><div class="topVideos">${recent.slice(0, 8).map(videoCard).join('')}</div></div>` : ''}
      </div>
    </div>`;
  }

  async function loadYoutube() {
    try {
      const response = await fetch(`${DATA_URL}?v=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (!data.channel?.statistics) throw new Error('youtube.json has no channel statistics');
      renderYoutube(data);
    } catch (error) {
      console.error('[Laxman Nepal] YouTube renderer failed:', error);
      const section = document.getElementById('youtube');
      if (section) section.querySelector('.desc')?.insertAdjacentHTML('afterend', '<div class="empty" style="margin-top:16px">YouTube data could not be loaded. The backend JSON will retry on the next page load.</div>');
    }
  }

  function init() {
    moveYoutubeBeforeApps();
    loadYoutube();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true }); else init();
})();
