# Feature: 002-practice-paging

Practice view: full-screen landscape window showing 4 measures with note-name rows, tap zones for paging.

## Requirements
- FR-1: "Practice" button enters an overlay occupying the viewport (fullscreen API + best-effort orientation lock to landscape).
- FR-2: One window = 2 consecutive measures, rendered fresh via abcjs from the loaded file's per-bar blocks (reuse header). Practice has its OWN size slider (#pfsize, top bar, caps at fit); entering copies the main slider's value. User correction 2026-11-15: measures sit side by side, 2 per window (was 4), slider present inside the view (was fit-to-screen only), Practice button lives in the top toolbar (was below the score).
- FR-3: Note-name rows always visible in practice view (reuse stampNames).
- FR-4: Tap right ~third → next 4 measures; tap left ~third → previous; arrow keys too. Bar-range indicator ("Bars 5–8 · 2/27"). ✕ exits (and exits fullscreen).
- FR-5: Structural tokens (|1,3 / :|2 / |: / :|) are stripped within windows to keep fragments parseable; bar comments retained.
- FR-6: Works per loaded file; empty last window never shown (last pages may hold fewer than 4 bars).

## Acceptance
- AC-1: Headless: practice view of hitchcock_full renders 2 bars with labels; paging changes window; practice slider changes size and never pages as a side effect; no console errors.
- AC-2: Chromium AND Firefox render identically in practice mode.
