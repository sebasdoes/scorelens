# Plan: 001-abc-folder-viewer

## Stack decision
- **Renderer**: abcjs 6.7.2, vendored `app/abcjs-basic-min.js` (MIT). Confirmed: stock abcjs has no note-name drawing, so names come from ABC annotation injection.
- **Serving**: existing `abctools-web` nginx:alpine, re-mounted to this repo: `/srv/app` (webroot) and `/srv/files` (`location /files/` with `autoindex_format json`, `.abc` filter). Upstream name → `scorelens-web:80`; oauth sidecar config updated accordingly.
- **Note-name algorithm** (modeled on Eskin's MIT `injectABCNoteNames`, rewritten self-contained):
  1. Split ABC into header (`K:` state) and body lines.
  2. Track current key (parse `K:Db maj`, `K:Am`, inline `[K:...]`; accidental order FCGDAEB).
  3. Scan music tokens left-to-right: `|` resets bar accidentals; `[A-Ga-g]` with optional `=^_` explicit accidental → effective name = explicit accidental, else key accidental.
  4. Skip/protect: quotes ("chords/text"), `!decoration!`, `%` comments, headers.
  5. Insert below-staff annotation `_"<name>"` before each note, including each note inside `[chords]`.
  6. Names: plain letter when natural-to-key; ♭/♯ prefix glyph when altered; `♮` for explicit naturals. E.g. `D` in Db → `D♭`; `^C` in C → `C♯`; `=E` in Db → `E♮`.
- **Size**: abcjs `scale` option fed by a range slider (1.0–3.0, default 2.0).
- **UI**: file <select> + refresh button; "Note names" checkbox; slider; render pane, black on white, `font-size` scales.

## Files
- `app/index.html` — the whole app (UI + injection + render).
- `app/abcjs-basic-min.js` — vendored.
- `nginx/default.conf` — webroot + JSON autoindex.
- `files/` — user's `.abc` files (mounted read-only); sample: `hitchcock_p1.abc`.
- `.gitignore` — files/* not committed? Commit sample only; runtime files stay in `files/`.

## Risks
- Annotation placement for dense chords — verified visually by user screenshot (ask early per user preference).
- JSON autoindex needs nginx ≥1.7 (any current image fine).
