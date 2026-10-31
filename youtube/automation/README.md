# Laxman Nepal Official — Daily Nepali Tech Shorts

A free-first, editable GitHub Actions pipeline that researches Nepali tech topics, asks Claude (or Groq) for one evidence-based Nepali Short, generates a vertical motion-graphics video and can publish it to YouTube Shorts, a Facebook Page Reel and an Instagram Professional Reel.

## Reality check

- GitHub Actions, FFmpeg, Python and Google Trends/News RSS can run without a monthly software subscription, within GitHub's free usage limits.
- Claude Pro does **not** include Claude API credits. Add `ANTHROPIC_API_KEY` to use Claude API; otherwise add `GROQ_API_KEY` for its free-tier API (subject to provider limits). Without either, the pipeline deliberately stops rather than inventing a script.
- Nepali voice: gTTS is the no-cost fallback; ElevenLabs is optional and requires its own API key/credits.
- YouTube requires Google Cloud project + YouTube Data API + OAuth refresh token. Uploads are free within API quota; newly created unverified API projects may have upload restrictions.
- Facebook Page Reels use Meta's Page video_reels upload flow. Instagram Reels require a Professional account connected to the Page and a publicly reachable video URL. Configure Cloudflare R2 public bucket settings for that URL. Meta permissions/app review may be required.
- No publishing happens until secrets are configured and `AUTO_PUBLISH=true`. Test with `publish=false` first.
- GitHub Actions free minutes/storage are quota-limited. This is not guaranteed unlimited compute or storage.

## Install

1. Merge this feature branch into `main` (or keep it as a branch and change the dashboard branch setting).
2. In GitHub → Settings → Secrets and variables → Actions, add the secrets listed below.
3. Enable Actions and run **Daily Nepali Tech Shorts → workflow_dispatch** with `publish=false` once.
4. Inspect the MP4 artifact and `output/latest.json`. Fix the script/voice/visuals in the dashboard or edit `config.json` and prompt file.
5. Set repository variable `AUTO_PUBLISH` to `true` only after all three platforms have been tested. Scheduled runs then publish automatically at 18:15 Nepal time.
6. Open `https://laxmannepal.com.np/youtube/automation/` after the branch is merged and published. Enter a fine-grained GitHub token with Actions: write and Contents: read permissions in the dashboard. It is stored in this browser only.

## GitHub Actions secrets

Required for AI generation: `GROQ_API_KEY` **or** `ANTHROPIC_API_KEY`.

Optional voice: `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`. Without these, gTTS Nepali voice is used.

YouTube: `YOUTUBE_CLIENT_SECRETS_JSON` (OAuth client JSON), `YOUTUBE_REFRESH_TOKEN`.

Meta: `META_PAGE_ACCESS_TOKEN`, `META_PAGE_ID`, `META_IG_USER_ID`, `META_GRAPH_API_VERSION` (e.g. `v23.0`). Token needs Page publishing permissions and access to the linked Instagram Professional account.

Instagram media hosting: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_PUBLIC_BASE_URL`. Set the bucket's public custom domain/base URL. This is needed because Instagram's standard publishing flow fetches video from a public URL.

## Dashboard

The dashboard can read the latest generated brief, edit the title/script, and dispatch a one-off generation/publishing run. A GitHub token is required to trigger workflows. Never paste API keys or Meta/Google tokens into the dashboard; put them only in GitHub Actions Secrets.

## Safety

The research stage collects source links, ranks fresh topics, and asks the model to cite factual claims. It skips when evidence is insufficient. Always review the first few outputs. Do not use copyrighted music or unlicensed footage. The default video is original motion graphics with no third-party footage; place a licensed music track at `assets/background.mp3` if desired.

## Schedule

Daily at 12:30 UTC (18:15 Asia/Kathmandu). Change cron in `.github/workflows/daily-shorts.yml` if needed.