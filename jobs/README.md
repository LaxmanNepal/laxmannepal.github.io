# Nepal Jobs Portal

Static GitHub Pages job portal at /jobs/.

## Current features
- Government, private, NGO/INGO, banking/finance, education, IT, health and other categories
- Keyword search
- Qualification, location, experience and remote filters
- Deadline countdown
- Job details modal
- Apply / official notice button
- Local bookmarks
- Responsive mobile UI
- SEO metadata

## Automatic maintenance
GitHub Actions runs every 6 hours and can also be started manually. It removes listings after their published deadline, records a `lastVerified` timestamp, and updates `jobs/last-updated.json`.

The automation intentionally does not scrape arbitrary sites or invent vacancies. New listings should come from an allowed RSS/API/feed or an explicitly approved public source, retaining the original source and application URL.

## Data quality
Each listing should contain `source`, `applyUrl`, `verified`, `deadline`, and `lastVerified`. Use the employer's official application URL whenever available.
