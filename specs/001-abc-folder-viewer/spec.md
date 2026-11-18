# Feature: Scorelens — read sheets from a folder with optional note names

## Purpose
Sebastiaan reads sheet music slowly (achromatopsia). He wants: open a `.abc` file that sits in a synced/mounted folder, see the rendered score large, and toggle letter names under every note.

## User stories
1. **Open a file from the folder**: When I open the site, I see the list of `.abc` files in the mounted folder; I click one and the score renders.
2. **Note names**: When I tick "Note names", every note gets its true pitch name (letter + accidental, e.g. `D♭`) below the notehead. Key signatures are respected (in `K:Db`, a written `D` shows as `D♭`); explicit accidentals in the ABC override the key; accidentals reset at barlines; names update in order left-to-right like real notation.
3. **Large notes**: A size control scales the notation; default is large (2×). Pure black on white, no color coding.
4. **Only me**: The site stays behind Pocket ID SSO.

## Requirements
- FR-1: `GET /` serves the app; `GET /files/` returns a JSON listing of `.abc` files only.
- FR-2: Rendering uses vendored abcjs (6.7.2, MIT). No CDN.
- FR-3: Note-name annotation is applied via ABC annotation injection (below-staff `_"name"`), key-aware, including mid-line `K:` changes and chords.
- FR-4: Size slider 1.0×–3.0×, default 2.0×; layout re-renders on change.
- FR-5: Multi-voice ABC (grand staff) renders both voices with names in both.

## Acceptance checks
- AC-1: Unauthenticated `curl https://scores.v.akiha.nl/` → 302 to `id.akiha.nl/authorize`.
- AC-2: Nginx serves index.html and the sample `.abc` directly (verified on the proxy network).
- AC-3: Note-name injection on a test ABC with `K:Db` yields `D♭` under written `D`, `F` under `F`, `C♮` under `=C`, chord tones named individually.
- AC-4: No published ports on the nginx or oauth containers.

## Out of scope (v1)
Playback, uploading, editing, saving, PDF export. The 600 MB abctools checkout stays on disk but is no longer served.
