# Tasks: 001-abc-folder-viewer

## Setup
- [ ] T1 Vendor abcjs 6.7.2 into `app/abcjs-basic-min.js` (jsdelivr, no CDN at runtime)
- [ ] T2 Write `nginx/default.conf`: webroot `/srv/app`, `location /files/` alias `/srv/files/`, `autoindex on; autoindex_format json;`
- [ ] T3 Sample file `files/hitchcock_p1.abc` (from /root/scores/hitchcock-page1/source.abc)

## Implement
- [ ] T4 `app/index.html`: fetch `/files/`, list `.abc` entries (name + mtime sorted desc)
- [ ] T5 Render on select: `ABCJS.renderAbc(paper, abc, {scale, staffwidth, paddingtop, colors})` — black-on-white
- [ ] T6 Note-name injection module (key parsing, barline accidental reset, chords, inline K:, annotations `_"name"`)
- [ ] T7 Verify injection logic in node against AC-3 cases (K:Db → D♭ under D, F stays F, =C → C♮)
- [ ] T8 Size slider 1.0–3.0 (default 2.0) re-renders live

## Deploy
- [ ] T9 Compose: rename service `abctools-web`→`scorelens-web`, new mounts (app, files, conf), remove abctools mount from caddy
- [ ] T10 Update `scores.cfg` upstream → `scorelens-web:80`, recreate sidecar + nginx
- [ ] T11 Verification gates: proxy-network fetch of index + files JSON; external 302→id.akiha.nl; no published ports; docker logs sidecar healthy
- [ ] T12 Ask user for screenshot (visual check of note-name placement) — per profile convention
