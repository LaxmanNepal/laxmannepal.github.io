# Nepali Typing Workspace — Implementation Plan

**Target:** https://laxmannepal.com.np/tools/nepali-tools/type-nepali/  
**Repository:** `LaxmanNepal/laxmannepal.github.io`  
**Approach:** preserve the existing static-site architecture; use free/open-source components and avoid a paid backend.

## Current-state audit

The tool is a standalone HTML/CSS/JavaScript page at `tools/nepali-tools/type-nepali/`. It is included in the existing site shell and is deployed through the repository's GitHub Pages workflow.

Current code already includes:
- Four mode controls: Google Input, Traditional, Romanized, and Voice Input.
- Suggestion buttons, keyboard navigation, and space-to-accept behavior.
- Browser-local draft saving, undo/redo, copy, download, clear, examples, and word/character counts.
- A Google Input Tools request with a limited local fallback.
- A hand-written transliteration table and a small direct-key mapping.
- Browser Web Speech API support when the browser exposes it.

Important gaps visible in the code:
- The Romanized conversion table is a lightweight heuristic, not a comprehensive Nepali transliteration engine.
- The Traditional mode's `DIRECT` map covers only a subset of keys and has not been validated against a documented standard layout.
- Google Input depends on a remote endpoint; network errors and delayed/out-of-order responses need predictable handling.
- Voice input is browser-dependent and must clearly communicate permission, unsupported-browser, and recognition-error states.
- The suggestion-selection issue has been fixed in multiple prior PRs, but a successful GitHub Actions deployment is not proof that the live UI regression is fixed.

## Phase 0 — Reproduce and lock down the existing bug (no new features yet)

### Regression scenario
1. Open the live tool in a clean browser session and clear the editor.
2. In Google Input mode, type `namaste` without a space.
3. Wait for suggestions, then click `नमस्ते`.
4. **Expected:** the entire unfinished Latin token is replaced with `नमस्ते`; no `namaste` remains before or after it.
5. Repeat using keyboard selection (Arrow keys/Tab and Enter where supported) and Space-to-accept.
6. Repeat after moving the caret into a word, after editing a word in the middle of a sentence, and after a delayed/out-of-order Google response.
7. Repeat the click test in Romanized mode.
8. Check the browser console for errors and verify the deployed page loaded the current version of `app.js`.

### Required regression tests
- Clicking a suggestion replaces the exact unfinished token once.
- A stale suggestion cannot replace text after the editor contents or selection changed.
- Selecting a suggestion does not lose editor focus or unexpectedly move the caret.
- Remote suggestions arriving late cannot overwrite suggestions for a newer token.
- Space and keyboard selection behave consistently; punctuation and adjacent text remain intact.
- Empty input, Unicode text, braces-protected English, undo/redo, and draft restoration remain intact.

**Gate:** do not start the workspace redesign until the selection regression is reproducible or explicitly marked “not reproduced,” the root cause is documented, and regression coverage passes. If the bug cannot be interactively tested from the development environment, keep it open for a live-browser check rather than declaring it fixed.

## Phase 1 — Stabilize typing engines

Keep each mode behaviorally distinct and label its capabilities honestly.

### Google Input
- Keep suggestions asynchronous and cancellable; guard against stale requests.
- Replace the full captured token and preserve the caret correctly.
- Keep a useful local fallback if the remote endpoint fails.
- Show connection/loading/fallback states without blocking typing.
- Request only the unfinished token for suggestions; never send the whole document.

### Romanized
- Replace the current ad-hoc transliteration with a well-tested, documented open-source Nepali transliteration implementation if a suitable license-compatible option is available.
- If no dependency meets the requirements, implement a clearly specified local engine with unit tests for vowels, consonants, aspirates, conjuncts, halant, matras, nasalization, punctuation, case, and common alternate spellings.
- Work offline and preserve ordinary English text when the user intends not to convert it.
- Keep suggestions and token replacement separate from the conversion engine.

### Traditional keyboard
- Select a documented Nepali keyboard layout and verify the mapping against its authoritative reference before implementation.
- Support the full printable key set, shifted keys, vowel signs, conjunct formation, virama/halant, punctuation, and backspace behavior.
- Add an optional on-screen keyboard/reference that follows the selected layout.
- Do not label a partial map as a complete “standard” layout.

### Voice input
- Feature-detect speech recognition and handle unsupported browsers gracefully.
- Handle microphone denial, recognition errors, interim/final results, stop/restart, and appending to existing text.
- Clearly state that speech recognition availability and processing depend on the browser/platform; do not promise offline voice input unless it is proven.

## Phase 2 — Professional workspace redesign

Build on the existing shared site header and static architecture.

- Clear workspace hierarchy: title, mode selector, focused editor, contextual suggestions, and compact action toolbar.
- Responsive layout with touch-friendly controls and no horizontal overflow on mobile.
- Editor status area with word/character counts, saved status, active mode, and voice/network status where relevant.
- More discoverable actions: undo, redo, copy, download, clear, and keyboard help.
- Keyboard accessibility: visible focus, semantic labels, live status announcements, and predictable Tab/Arrow/Enter behavior.
- Respect reduced-motion preferences and maintain readable contrast.
- Add a compact settings panel for editor font size and optional autosave behavior; do not add accounts or a server-side document store.
- Preserve the site's existing navigation and shared visual system.

## Phase 3 — Writing tools

Only after the core modes pass acceptance tests:
- Find/replace, select-all, and clear-with-confirmation for non-empty documents.
- Download UTF-8 plain text with a sensible filename; optionally add print-friendly output.
- Document templates for common Nepali letters, निवेदन, office applications, and Loksewa practice.
- Separate utilities for Roman Nepali ↔ Unicode and Preeti/Kalimati legacy-font conversion. Treat legacy-font conversion as its own encoding problem, not as a typing mode.
- Optional typing practice with WPM/CPM and accuracy, calculated locally.

## Phase 4 — Offline, performance, and discoverability

- Keep the core editor and local typing modes functional without network access.
- Add a PWA/offline cache only after cache invalidation and update behavior are tested.
- Use lightweight assets and avoid introducing a large framework for a single tool.
- Add SEO content explaining the distinct typing modes, keyboard layout, examples, and FAQs.
- Analytics, if added, should collect only aggregate events (mode selected, copy/download action, errors, performance); never record typed text, candidate words, or document contents.

## Suggested implementation sequence and PR boundaries

1. **PR A — Regression coverage and bug diagnosis:** test the current suggestion replacement issue; add automated regression coverage or a documented manual test fixture. Make only the smallest required bug fix.
2. **PR B — Typing engine reliability:** improve Google request lifecycle and Romanized engine with tests.
3. **PR C — Complete Traditional layout:** implement a verified layout and its reference keyboard.
4. **PR D — Voice reliability and accessibility:** improve browser capability/error states and keyboard accessibility.
5. **PR E — Workspace redesign:** restructure layout and controls without changing tested engine behavior.
6. **PR F — Writing features:** add find/replace, templates, and legacy-font converters as separate, testable modules.
7. **PR G — PWA, SEO, and privacy-preserving analytics:** only after functional acceptance is met.

Each implementation PR should include: scope, screenshots or a clear before/after description, tests run, known limitations, and a deployment check. Merge only after review; then wait for GitHub Actions to succeed and verify the live URL and cache-busted assets.

## Definition of done

- All four modes have documented, distinct behavior and explicit browser/network requirements.
- Regression and unit tests pass for suggestion replacement, caret/range behavior, conversion rules, keyboard mappings, and failure states.
- The page works at desktop and mobile widths, supports keyboard-only use, and has no console errors in supported browsers.
- Local typing remains available without a network; remote suggestions fail gracefully.
- No typed text is sent to analytics or persisted remotely.
- GitHub Pages deployment succeeds, the live site serves the expected build, and the original bug is retested on the deployed page before it is marked fixed.
