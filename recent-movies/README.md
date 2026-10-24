# Recent Movies catalogue

Static movie discovery page at https://laxmannepal.com.np/recent-movies/ .

## Automatic data updates

The scheduled GitHub Actions workflow `.github/workflows/recent-movies.yml` refreshes `data/recent-movies.json` daily using The Movie Database (TMDB) API.

1. Create a TMDB API key from your TMDB account's API settings.
2. In this repository, open **Settings → Secrets and variables → Actions → New repository secret**.
3. Name the secret `TMDB_API_KEY` and paste the key value.
4. Run **Actions → Refresh recent movies catalogue → Run workflow** once to verify the setup.

The page intentionally does not expose the API key in browser JavaScript. The catalogue is a static JSON file, so the website remains fast and does not require a server-side runtime. Data includes Nepali, Hindi, Tamil, Telugu, Malayalam, Kannada and English-language films, plus upcoming, now-playing and popular listings. Categories are best-effort metadata; TMDB release information may not confirm screenings at a particular Nepal cinema.

Attribution: Movie data and posters are provided by TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB.
