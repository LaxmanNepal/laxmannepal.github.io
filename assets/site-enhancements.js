(() => {
  const DATA_URL = './data/youtube.json';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const fmt = (n) => {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return '—';
    return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(x);
  };
  const dateFmt = (v) => v ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(v)) : '—';
  const escapeHtml = (s) => String(s ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

  function moveAppsBeforeYoutube() {
    const apps = document.getElementById('apps');
    const youtube = document.getElementById('youtube');
    if (apps && youtube && apps !== youtube && youtube.parentNode) youtube.parentNode.insertBefore(apps, youtube);
    const links = $('#links');
    if (links) {
      const youtubeLink = $('a[href="#youtube"]', links);
      const appsLink = $('a[href="#apps"]', links);
      if (youtubeLink && appsLink) links.insertBefore(appsLink, youtubeLink);
    }
  }

  function renderYoutube(data) {
    const section = document.getElementById('youtube');
    if (!section || !data) return;
    const stats = data.channel?.statistics || data.statistics || {};
    const videos = Array.isArray(data.popularVideos) ? data.popularVideos : (Array.isArray(data.videos) ? data.videos : []);
    const recent = Array.isArray(data.recentVideos) ? data.recentVideos : [];
    const list = videos.length ? videos : recent;
    const channelTitle = data.channel?.title || data.channelTitle || 'YouTube Channel';
    const channelUrl = data.channel?.url || data.channelUrl || 'https://www.youtube.com/@laxmannepalofficial';
    const updated = data.lastUpdated || data.updatedAt;

    section.innerHTML = `
      <div class="wrap">
        <div class="sectionHead reveal in">
          <div><div class="kicker">YouTube</div><h2 class="title">My channel, in real data.</h2></div>
          <div class="desc">Live public channel statistics and the videos people are watching most. Data is read from the repository JSON; your API key never reaches visitors.</div>
        </div>
        <div class="stats reveal in">
          <div class="stat glass"><b>${fmt(stats.subscriberCount ?? data.subscriberCount)}</b><span>Subscribers</span></div>
          <div class="stat glass"><b>${fmt(stats.viewCount ?? data.viewCount)}</b><span>Total views</span></div>
          <div class="stat glass"><b>${fmt(stats.videoCount ?? data.videoCount)}</b><span>Videos</span></div>
          <div class="stat glass"><b>${fmt(list.length || data.videoCount)}</b><span>Featured videos</span></div>
        </div>
        <div class="youtubeDataPanel glass reveal in" style="margin-top:16px;padding:18px;border-radius:24px">
          <div style="display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap;margin-bottom:14px">
            <div><strong style="font-family:Poppins">${escapeHtml(channelTitle)}</strong><div class="updated">Updated ${dateFmt(updated)}</div></div>
            <a class="btn" href="${escapeHtml(channelUrl)}" target="_blank" rel="noopener">Open channel ↗</a>
          </div>
          <div class="topVideos" id="liveTopVideos">
            ${list.slice(0, 12).map(v => {
              const title = v.title || v.snippet?.title || 'Untitled video';
              const thumb = v.thumbnail || v.thumbnails?.high?.url || v.snippet?.thumbnails?.high?.url || v.snippet?.thumbnails?.medium?.url || '';
              const views = v.views ?? v.statistics?.viewCount ?? 0;
              const likes = v.likes ?? v.statistics?.likeCount ?? 0;
              const comments = v.comments ?? v.statistics?.commentCount ?? 0;
              const url = v.url || (v.videoId ? `https://www.youtube.com/watch?v=${encodeURIComponent(v.videoId)}` : '#');
              return `<a class="topVideo" href="${escapeHtml(url)}" target="_blank" rel="noopener"><img class="thumb" loading="lazy" src="${escapeHtml(thumb)}" alt=""><div><b>${escapeHtml(title)}</b><span>${fmt(views)} views · ${fmt(likes)} likes · ${fmt(comments)} comments</span></div></a>`;
            }).join('') || '<div class="empty">YouTube data is waiting for the next successful Action run.</div>'}
          </div>
        </div>
      </div>`;
  }

  async function loadYoutube() {
    try {
      const response = await fetch(`${DATA_URL}?v=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      renderYoutube(data);
    } catch (error) {
      console.warn('YouTube JSON unavailable:', error);
    }
  }

  function init() {
    moveAppsBeforeYoutube();
    loadYoutube();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true }); else init();
})();
