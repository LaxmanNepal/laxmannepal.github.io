# Complete Nepali Typing Workspace — Implementation Roadmap

**Target page:** https://laxmannepal.com.np/tools/nepali-tools/type-nepali/  
**Repository:** `LaxmanNepal/laxmannepal.github.io`  
**Planning branch:** `plan/nepali-typing-complete-roadmap-2026`  
**Scope:** Complete end-to-end upgrade; all audiences; offline-first and local privacy by default; AI optional and opt-in.  
**Architecture rule:** Keep the site static and lightweight. Reuse the existing shared shell, CSS conventions, GitHub Pages deployment, and plain HTML/CSS/JavaScript where practical. No account system, mandatory backend, paid API, or large framework.

> **Status update (25 October 2026):** This document began as a plan. The implementation has since been delivered in multiple PRs, with Chromium browser tests and GitHub Pages deployment checks. The status below distinguishes completed work from remaining limitations.

## 0. Implementation status (25 October 2026)

### Implemented and merged
- [x] Fixed the mid-word suggestion range bug and added range regression tests.
- [x] Added a Chromium browser-test workflow and deployment-time regression checks.
- [x] Added a larger local Nepali lexicon and ranked Romanized candidates, with the earlier converter as a fallback.
- [x] Made Google suggestions opt-in and off by default; stale remote requests are aborted and range-checked.
- [x] Added offline-first PWA caching for the typing workspace and local conversion.
- [x] Added local named documents, templates, find/replace, print, delete-saved-text and local learned suggestions.
- [x] Added native share support with a copy fallback.
- [x] Added a separate Nepali typing practice page with WPM, CPM, accuracy and error metrics.
- [x] Added a separate Preeti ↔ Unicode converter with upstream licence and attribution.
- [x] Improved voice error handling, listening-state accessibility and saving voice transcripts to local documents.
- [x] Added responsive layout checks, FAQ content, Open Graph metadata and SoftwareApplication/FAQPage structured data.

### Remaining / deliberately not claimed complete
- [ ] **Traditional direct-key layout:** the current mapping is still partial. It must remain labelled partial until checked against an authoritative keyboard layout and tested end-to-end.
- [ ] **Real-device validation:** automated browser tests run in Chromium. Manual testing on iOS Safari, Android browsers, native IMEs, assistive technologies and real microphones remains outstanding.
- [ ] **Romanization coverage:** the local lexicon improves ranking, but dialects, names and ambiguous spellings still need a broader test corpus. Suggestions are candidates, not guaranteed translations.
- [ ] **Legacy font coverage:** the converter targets Preeti. It does not claim support for Kantipur, PCS Nepali or custom legacy fonts, and mixed English inside Preeti input needs careful review.
- [ ] **Cross-browser offline validation:** the service worker is tested in Chromium; Safari and Firefox offline/update behavior should be checked on real devices.

## 1. Current implementation inspected

Current page files:
- `tools/nepali-tools/type-nepali/index.html`
- `tools/nepali-tools/type-nepali/app.js`
- `tools/nepali-tools/type-nepali/style.css`

Existing capabilities include four mode buttons (Google Input, Traditional, Romanized, Voice), candidate buttons, a local draft in `localStorage`, undo/redo, copy/download/clear, sample phrases, word/character counts, a Google Input Tools request, a small hand-written transliteration map, a partial direct-key map, and browser Web Speech API voice recognition.

### Gaps found in code review

1. **Suggestion replacement depends on a captured range.** `getCurrentWord()` captures the token prefix before the caret as `word`, while its `end` can extend across the rest of the token. `acceptCandidate()` then compares the complete editor slice with that prefix. A caret placed inside a word can therefore make the guard fail.
2. **Keyboard behavior is inconsistent with the help text.** Arrow keys and Tab update the highlighted item, and Space commits, but there is no explicit Enter-to-accept handler. This needs a deliberate, documented interaction contract.
3. **Remote results need stronger range identity.** The callback checks the word and request ID, but regression tests must also cover caret/range changes and the same token appearing in different positions.
4. **Romanized conversion is heuristic.** The current maps cannot reliably cover Nepali orthography, conjuncts, halant, nasalization, spelling variants, and all punctuation.
5. **Traditional mode is partial.** The `DIRECT` map is a small subset and should not be described as a complete standard layout until validated against an authoritative layout.
6. **Voice input is platform-dependent.** Permission denial, unsupported browsers, interim/final transcript handling, and browser/network processing must be clearly communicated.
7. **Privacy language needs to match implementation.** Local drafts are stored in browser storage; Google suggestions send the current unfinished token to a third party; voice recognition may be processed by the browser/provider. These are different data flows and must be disclosed separately.
8. **Offline claim must be qualified.** Local editor behavior can work offline, but remote suggestions, external icon fonts, and speech recognition may not. A PWA cache needs version/update tests before being advertised as offline-ready.

## 2. Existing bug — reproduction result and first gate

### Isolated reproduction already run

An isolated Node.js probe using the current `getCurrentWord()` range logic reproduced a concrete failure:

- Text: `hello namaste world`
- Caret: between `nama|ste`
- Captured range: `word = "nama"`, `start = 6`, `end = 13`
- Actual editor slice: `"namaste"`
- Current acceptance guard: `"namaste" === "nama"` → **false**
- Result: candidate acceptance is rejected when the caret is inside the token.

This is a code-level reproduction of a range-handling defect, not an interactive reproduction on the deployed page. The exact original user-reported click symptom still requires a browser-level run against the current live build.

### Phase 0 — reproduce before changing behavior

**Do not start redesign/features until this phase is complete.**

1. Open the live URL in a clean browser profile and record the loaded `app.js` URL/version.
2. Test Google Input: type `namaste`, wait for local and remote candidates, click `नमस्ते`.
3. Repeat with caret at the end, in the middle of the word, and after moving to another word in a sentence.
4. Repeat after changing text while a Google request is pending; throttle/offline the network to force late responses and errors.
5. Repeat in Romanized mode, after undo/redo, after restoring a draft, and with braces-protected English.
6. Test Space, Tab, Shift+Tab, ArrowUp/ArrowDown, Enter, mouse click, punctuation, selection replacement, and IME/composition input.
7. Capture expected/actual text, caret position, mode, request timing, browser, console errors, and asset version. Do not store typed user content in analytics or issue logs.
8. Add a minimal deterministic regression test for the range failure before applying the fix. Then add browser-level coverage for the real event path.
9. Fix the smallest root cause, re-run the tests, merge only after review, wait for deployment, and repeat the same cases on the deployed URL.

**Phase 0 acceptance:** test results document the original failure and its root cause; automated tests fail before the fix and pass after it; no fix is declared successful based only on a green workflow.

## 3. Product goals and non-goals

### Goals
- Reliable Unicode Nepali typing for casual users, students, Loksewa candidates, teachers, office workers, journalists, and professional writers.
- Distinct, honest behavior for each typing mode.
- Offline local typing, local-only drafts, export without an account, and transparent privacy controls.
- Accessible desktop and mobile workspace that feels part of Laxman Nepal rather than a separate app.
- Reusable small modules that can support companion Nepali tools without coupling all features into one large script.
- Optional AI assistance that is disabled by default and never silently uploads a document.

### Non-goals
- No mandatory login, cloud sync, server-side document storage, or paid AI requirement.
- No claim that browser speech recognition is offline unless a supported offline implementation is verified.
- No promise of perfect automatic spelling/grammar correction.
- No combining Preeti/Kalimati legacy font conversion with Unicode transliteration; they are separate encoding workflows.

## 4. Target architecture

Keep the current static route and shared shell. Refactor the page JavaScript into small, testable files only as needed:

- `app.js`: page orchestration and UI events.
- `core/editor-state.js`: token/range handling, caret-safe edits, undo/redo.
- `engines/romanized.js`: deterministic offline Romanized-to-Unicode conversion.
- `engines/google-input.js`: optional remote suggestions, request lifecycle and local fallback.
- `engines/traditional-layout.js`: documented keyboard mapping and key composition.
- `engines/voice.js`: feature detection and speech-recognition lifecycle.
- `features/templates.js`: local document templates.
- `features/typing-practice.js`: local timer, accuracy and speed metrics.
- `features/privacy-settings.js`: per-feature network/autosave preferences.
- `style.css`: workspace styles consistent with the existing design system.

These are proposed module boundaries, not a requirement to create every file upfront. Start with the smallest extraction that enables tests. Avoid a build step unless the repository already provides one that fits.

### Dependencies policy
- Prefer native browser APIs and small open-source libraries with a compatible license.
- Before adopting a transliteration or legacy-font library, record source, license, maintenance status, bundle size, and test coverage.
- Pin versions if a dependency is added; do not load unpinned runtime scripts from random CDNs.
- Do not add a dependency solely for a feature that can be implemented and tested reliably with existing browser APIs.

## 5. Delivery phases and detailed requirements

### Phase 0 — Bug reproduction and regression lock (blocking)

Deliverables:
- Repro notes and expected/actual matrix.
- A regression fixture for token/range and caret handling.
- Browser-level test for candidate click and keyboard acceptance.
- Minimal bug fix only after a failing test exists.
- Clear record of what has and has not been verified on the live site.

### Phase 1 — Core editor correctness

- Treat the selected token as a stable range with start/end, original text, and selection identity.
- Invalidate candidates whenever text, selection, mode, or relevant request changes.
- Never apply a candidate if its captured range no longer matches the current document.
- Preserve the caret and selected range for replacement; do not jump to document end unless that is the expected action.
- Support selected-text replacement, caret inside a word, punctuation, line breaks, Unicode text, braces-protected segments, undo/redo, and restored drafts.
- Add explicit Enter-to-accept only if it does not interfere with normal textarea newline entry; document the shortcut and provide a predictable modifier/setting if needed.
- Use a single source of truth for the selected candidate; keep visual highlight and actual accepted candidate synchronized.
- Make asynchronous responses abortable where possible and ignore responses whose request, mode, token, selection, or document version is stale.
- Ensure timers are cleared in success and failure paths.
- Keep local typing functional if Google Input is unreachable.

**Exit criteria:** all suggestion/range tests pass, including the mid-token reproduction above; no duplicate or partial token remains; caret and undo history remain correct.

### Phase 2 — Reliable offline Romanized engine

- Define a documented transliteration scheme and expected output for vowels, short/long vowels, consonants, aspirates, retroflex letters, conjuncts, halant, matras, anusvara/chandrabindu, visarga, punctuation, digits, capitalization, and common alternate spellings.
- Prefer a suitable maintained open-source implementation after license and quality review. If none meets requirements, use a local rule-based engine with comprehensive unit tests.
- Separate conversion rules from candidate UI and editor mutation.
- Make the conversion behavior explicit: live composition, word-on-space commit, or preview-and-accept. Do not mix inconsistent behaviors across modes.
- Provide an easy way to preserve English words and names, including the existing brace convention; make the convention visible and accessible.
- Include a correction/exception dictionary stored locally and editable/resettable by the user.
- Avoid silently converting ambiguous words when confidence is low; show alternatives or preserve input.
- Include examples and a short keyboard/phonetic reference.

**Exit criteria:** deterministic unit tests cover common Nepali phrases and edge cases; all local conversions work with network disabled.

### Phase 3 — Complete Traditional keyboard mode

- Choose a specific documented layout (for example, the exact Unicode Nepali keyboard layout the product will support) and cite its authoritative mapping reference in the code/docs.
- Verify all unshifted and shifted printable keys, vowels/matras, punctuation, digits, halant, conjunct behavior, and backspace.
- Handle keydown/input/composition events without double-inserting text or breaking paste, undo, accessibility tools, and mobile virtual keyboards.
- Add an optional on-screen keyboard map that matches the selected layout and exposes shifted layers.
- Let users see the active layout name; do not label an incomplete map “standard.”
- Add tests for every key mapping and multi-key composition.

**Exit criteria:** the mapping matrix passes; typing, paste, deletion, selection, and undo work across supported browsers.

### Phase 4 — Voice mode that communicates limits

- Feature-detect `SpeechRecognition` and `webkitSpeechRecognition`; never show an active control when unsupported.
- Handle denied permission, no microphone, unavailable network/provider, no-speech, aborted, and service-not-allowed states.
- Keep interim text visually distinct from committed transcript if the API permits it; prevent repeated transcript concatenation on multiple result events.
- Define append/replace behavior when a session starts and stops.
- Make start/stop state accessible to screen readers and keyboard users.
- Explain that browser speech may be sent to the browser/vendor service and may require internet; it is not included in the offline guarantee.
- Do not record audio or transcripts beyond what is necessary to populate the current editor.

**Exit criteria:** each error has a recoverable message; supported and unsupported browsers behave clearly; transcript duplication tests pass.

### Phase 5 — Professional workspace UI and accessibility

- Retain the site shared header/navigation and existing URL; do not introduce a second site shell.
- Make the editor the visual focus with a compact mode switcher, clear suggestion strip, readable status line, and low-clutter action bar.
- Add visible saved/offline/remote-suggestion/voice status; status labels must reflect real state, not assumptions.
- Add configurable font size and line height, optional wrap behavior, focus mode, and clear confirmation.
- Provide find/replace, select all, copy, download, print, and undo/redo. Keep destructive actions confirmable and undoable where practical.
- Support mobile touch targets, narrow viewports, virtual keyboards, landscape, and no horizontal overflow.
- Ensure keyboard-only operation, visible focus, meaningful labels, sensible tab order, high contrast, reduced motion, and screen-reader announcements.
- Use proper semantic controls rather than clickable non-semantic spans.
- Test Nepali font fallback on Windows, Android, iOS, and Linux; do not bundle fonts without checking licensing and performance.

**Exit criteria:** desktop/mobile visual checks and keyboard-only accessibility checks pass; no critical accessibility regressions.

### Phase 6 — Local documents, templates and export

- Support multiple named documents in browser storage with create, rename, duplicate, delete, and restore.
- Use a clear local-storage quota/error state; offer export before storage is cleared or unavailable.
- Store only user-created drafts/settings locally. Provide “Delete all local data” with clear explanation and confirmation.
- Add templates for निवेदन, leave application, office letter, school application, CV/resume outline, meeting minutes, and Loksewa practice. Use placeholders and editable text, not pre-filled personal data.
- Provide UTF-8 `.txt` export and print-friendly output first; consider `.docx` or PDF only if a lightweight, license-compatible, client-side path can be tested.
- Use descriptive filenames and preserve Nepali Unicode.
- Add find/replace with safe handling of regex-like characters; literal search is the default.
- Add word/character/paragraph counts and optional reading/typing metrics without uploading content.

**Exit criteria:** templates open/edit/export correctly; drafts survive reload; deletion actually removes local records; exports round-trip Nepali Unicode correctly.

### Phase 7 — Typing practice and learning

- Add practice passages by difficulty and topic, with editable custom passages.
- Calculate local WPM/CPM, accuracy, error count, elapsed time, and optional consistency; document the formula used.
- Use a stable definition of “correct character” that handles Devanagari combining marks and grapheme clusters correctly.
- Offer 1/3/5/10-minute practice and untimed practice; never punish users for pausing or changing font size.
- Add downloadable practice text and printable lesson sheets.
- Add beginner help for phonetic typing and a separate Traditional layout tutorial.
- Do not upload passages or user performance by default.

**Exit criteria:** timer and scoring tests cover paste, backspace, repeated characters, combining marks, pause/resume, and custom passages.

### Phase 8 — Separate Nepali text utilities

Ship as separate routes/modules after core reliability, each with its own tests and page description:

- Roman Nepali ↔ Unicode converter.
- Preeti ↔ Unicode converter.
- Kalimati/legacy-font converter only after confirming the exact mapping and license/attribution requirements.
- Unicode inspector and cleanup: normalize whitespace, remove accidental zero-width characters with preview, punctuation spacing, quote/bracket checks, and copy.
- Nepali typing test and keyboard-layout reference.
- Letter/template library.
- Optional Nepali OCR only after a fully local or clearly opt-in implementation is available and quality/privacy are assessed.

**Important:** legacy font conversion must be tested with real sample documents from multiple sources. Do not promise lossless conversion without evidence; preserve the original text and provide before/after preview.

### Phase 9 — Offline-first PWA and performance

- Core editor, local Romanized engine, Traditional mode, templates, typing practice, and exports must work offline.
- Use a service worker only after defining a versioned asset manifest, cache update strategy, stale-cache recovery, and “new version available” behavior.
- Cache only the page and required static assets; do not cache remote suggestions, user drafts in shared caches, voice data, or AI responses by default.
- Test first visit offline, repeat visit offline, update deployment, old cache, quota pressure, and recovery from a failed update.
- Remove or locally bundle nonessential runtime assets that otherwise break offline use, while preserving licensing.
- Measure page weight and interaction performance on a low-end mobile device and slow connection.
- Avoid claiming “works fully offline” unless every included feature and dependency is tested in airplane mode.

**Exit criteria:** defined offline feature matrix passes; cache updates cannot trap users on a broken build; page remains lightweight.

### Phase 10 — Privacy, security and optional AI

**Default behavior**
- No account, server-side documents, content analytics, or hidden upload.
- Autosave is local-only and visibly configurable; local data deletion is available.
- No text, document contents, candidate words, audio, or templates are sent to analytics.
- Google Input suggestions remain an explicit remote mode. Explain that only the unfinished token is sent and offer local-only mode as the default or an obvious one-click choice.
- Make remote suggestions opt-in and remember that choice locally.
- Add a simple privacy/data-flow panel showing which feature uses local processing, network access, microphone access, and browser storage.

**Optional AI**
- Disabled by default and separated from core typing.
- AI may help rewrite, summarize, proofread, or adjust tone only after the user explicitly selects text and confirms sending it to a named provider.
- Never send the whole document by default; show the exact selected text and destination before submission.
- Do not require an API key for core features. If a bring-your-own-key option is ever considered, store it only in session memory by default, never in source code, URL, analytics, or synced storage.
- Show provider, data handling caveat, rate/cost warning, and clear cancel action. Do not make unverified privacy guarantees about third-party services.
- Prefer local dictionaries/rules for spelling hints. AI-generated edits must be suggestions, never silent edits.

**Exit criteria:** network inspection confirms no content requests unless the user invokes a remote feature; AI remains off until consent; delete-local-data control works.

### Phase 11 — SEO, discoverability and maintainability

- Keep the canonical route and shared site navigation.
- Update page title/description and structured metadata only if accurate; avoid claims of perfect translation, complete offline voice, or guaranteed grammar correction.
- Add clear explanations of each mode, supported keyboard layout, privacy, offline limits, FAQs, and accessible examples.
- Add internal links to the separate Nepali tools and practice resources.
- Keep content useful even when JavaScript is unavailable; provide a clear fallback message.
- Document how to add a new mode, template, or converter without coupling it to unrelated logic.

## 6. Test strategy

### Automated tests
- Pure unit tests for transliteration rules, keyboard mapping, word/token range calculation, caret replacement, undo/redo history, and typing metrics.
- Regression test reproducing the mid-token acceptance failure; assert it fails against the current logic and passes after the fix.
- Browser tests for suggestion click/keyboard flows, stale remote response, error fallback, storage, mode switching, voice states, export, and responsive overflow.
- Accessibility checks for labels, focus, keyboard navigation, and live status.
- Use the repository's existing CI conventions. If no test runner exists, introduce the smallest maintainable setup and explain its CI/runtime cost in the PR.

### Manual matrix
- Browsers: current Chrome/Edge, Firefox, Safari where available.
- Devices: desktop keyboard, Android touch/virtual keyboard, iPhone/iPad where available.
- Network: online, slow, offline, remote endpoint failure, permission denied.
- Text: short and long Nepali, mixed English, punctuation, digits, emoji, multiple paragraphs, combining marks, selected ranges, braces-protected text.
- Storage: fresh session, restored draft, full/blocked storage, clear local data.
- Accessibility: keyboard-only, screen reader spot-check, zoom 200%, reduced motion.

### Release verification checklist
1. Tests pass on the proposed branch.
2. Review the diff for scope, privacy, licensing, console errors, and accidental unrelated changes.
3. Open a focused PR; do not merge the entire roadmap as one implementation.
4. Wait for required GitHub Actions checks to complete successfully.
5. Verify the deployment commit matches the merged commit.
6. Open the live page and confirm the new asset version is served.
7. Repeat the original bug reproduction on the live URL and record browser/device/result.
8. Only then mark the specific bug fixed. A green CI workflow alone is not proof of live behavior.

## 7. Recommended implementation PR sequence

1. **PR 1 — Suggestion bug reproduction, regression tests, minimal fix.** No redesign or new tools.
2. **PR 2 — Editor state and asynchronous suggestion lifecycle.** Range identity, request cancellation, stale-response safety, undo/redo integrity.
3. **PR 3 — Romanized engine.** Documented scheme, local unit tests, correction dictionary, offline operation.
4. **PR 4 — Verified Traditional layout.** Authoritative mapping, shifted keys, reference keyboard, complete mapping tests.
5. **PR 5 — Voice reliability and accessibility.** Permission/error states, transcript correctness, accessible controls.
6. **PR 6 — Workspace redesign.** Responsive editor, action bar, status, settings, focus/accessibility.
7. **PR 7 — Local documents, templates, find/replace, export.**
8. **PR 8 — Typing practice and educational resources.**
9. **PR 9 — Separate converters and Unicode utilities.** Each converter independently tested.
10. **PR 10 — Offline/PWA and performance.**
11. **PR 11 — Privacy controls and optional AI integration.** Only after privacy/data-flow review.
12. **PR 12 — SEO, documentation and final cross-browser verification.**

Each implementation PR must stay small enough to review, contain tests and known limitations, and include its own deploy/live verification record.

## 8. Definition of complete

The tool is complete only when:
- The reported bug is reproduced or its non-reproduction is documented, its root cause is understood, and regression tests pass.
- All modes have clear, distinct, verified behavior and published limitations.
- Core typing, drafts, exports, and practice work offline.
- No typed content is silently uploaded or included in analytics.
- Optional remote/AI features require clear user choice.
- Traditional mappings and legacy-font converters are backed by documented references and test fixtures.
- Desktop/mobile, keyboard-only, and supported browser checks pass.
- GitHub Actions deployment succeeds and the live page is retested after deployment.
- User-facing documentation accurately describes what is local, remote, offline, and optional.
