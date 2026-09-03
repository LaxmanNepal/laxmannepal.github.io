import json
from xml.sax.saxutils import escape

BASE = 'https://apps.laxmannepal.com.np'
urls = [
    ('/', 1.0, 'daily'),
    ('/youtube/', 0.95, 'daily'),
    ('/apps/', 0.9, 'weekly'),
    ('/about/', 0.7, 'monthly'),
]

# Keep the app directory and sitemap in sync. Only online deployments are indexed.
try:
    with open('data/apps.json', encoding='utf-8') as f:
        app_data = json.load(f)
except Exception:
    app_data = {}

for app in app_data.get('apps', []):
    path = app.get('url', '')
    if app.get('status') != 'online' or not path.startswith(BASE + '/'):
        continue
    relative = path[len(BASE):]
    priority = 0.8 if app.get('featured') else 0.7
    freq = 'daily' if app.get('category') in {'Finance', 'Media'} else 'weekly'
    urls.append((relative, priority, freq))

# Add individual YouTube video pages when the dataset provides stable IDs.
try:
    with open('data/youtube.json', encoding='utf-8') as f:
        yt_data = json.load(f)
except Exception:
    yt_data = {}

seen = set(u[0] for u in urls)
for videos in (
    yt_data.get('popularVideos') or [],
    yt_data.get('recentVideos') or [],
    yt_data.get('latestVideos') or [],
):
    for video in videos:
        vid = video.get('id') or video.get('videoId')
        if vid:
            path = f'/youtube/video/?v={vid}'
            if path not in seen:
                urls.append((path, 0.65, 'monthly'))
                seen.add(path)

lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
]
for path, priority, freq in urls:
    lines.append(
        f'  <url><loc>{escape(BASE + path)}</loc><changefreq>{freq}</changefreq><priority>{priority}</priority></url>'
    )
lines.append('</urlset>')

with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f'Generated {len(urls)} URLs')
