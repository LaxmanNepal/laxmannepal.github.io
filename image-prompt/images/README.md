# Image Prompt Preview Images

This folder stores optional visual previews for the `/image-prompt/` library.

## Filename mapping

Each image filename must match the prompt ID:

- Prompt `#120` → `120.webp`
- Prompt `#119` → `119.webp`
- Prompt `#1` → `1.webp`

The website automatically looks for `/image-prompt/images/{prompt-id}.webp`.

## Recommended format

- Aspect ratio: **9:16**
- Format: **WebP**
- Suggested width: **768–1024 px**
- Keep files reasonably compressed for fast loading
- Avoid putting important text near the top/bottom edges

If a preview does not exist yet, the website shows a placeholder instead of a broken image.

## Google Flow workflow

1. Open the prompt library.
2. Click **Generate in Flow** on a prompt.
3. The prompt is copied and Google Flow opens in a new tab.
4. Paste the prompt into Flow and generate the image.
5. Download the result.
6. Rename it to the prompt ID, for example `120.webp`.
7. Upload it into this folder.
8. After GitHub Pages deploys, the preview appears automatically.

The site does not use a Gemini API key and does not attempt to automate Google Flow's private generation UI.