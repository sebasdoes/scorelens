# Scorelens

Scorelens is a self-hosted web app for reading ABC sheet music. I built it
because I read music slowly: I have achromatopsia, standard sheet music on a
tablet is small, and parsing dense notation takes me much longer than it takes
others. So instead of fighting with printed pages, I have a machine-readable
version of the piece, rendered exactly the way I need it — one measure at a
time, filling the screen, with the note names written under the notes.

The project started with a piano arrangement of Yorushika's Hitchcock that I
transcribed in ABC. Two more arrangements and a lot of UI iteration later, the
app has grown into a complete practice tool: it plays the music, it can listen
to my digital piano while I play along, and it keeps up with me while I read.

## Features

The main page lists the ABC files in a mounted folder and renders the selected
score, scaled to fill the screen width on any device. A toggle puts the note
name under every note head — the letter and the accidental, so an F♯ shows up
as "F♯" — which turns each measure into something I can read almost like
text.

Practice mode is the core of it. The screen shows one, two, or three measures
at a time (a small slider picks the count), filled edge to edge, with tap
navigation on the left and right. A voice toggle switches between RH, LH, and
a properly aligned two-staff grand staff view.

Every piece can be played back. The browser synthesizes the piano from the ABC
data — no MP3 files, no external soundfont CDN, the sound samples are served
from the app itself. In practice mode, playback follows the window: as soon as
you move to the next measure, the audio moves with you.

Three themes are built in — White, Dark, and a High Contrast mode that is
pure black with white notes — and the choice persists between visits. For
extra accessibility, everything on the score that conveys information (hit
marks, feedback, the current position) is text and ticks. I deliberately never
encode meaning in color, because color doesn't work for me at all.

## The piano link

The most fun part: Scorelens talks to my Yamaha P-105 digital piano over Web
MIDI. The piano plugs into the tablet with a cheap OTG cable, Chrome asks for
permission once, and from then on the page and the instrument are connected.

Three things happen when the piano is connected:

- **Duet mode.** The play button stops playing the staff I'm reading and
  instead plays the *other* one. If I'm reading the right hand, Scorelens
  plays the left hand along with me — a patient accompanist that never gets
  tired of waiting.
- **Auto-advance.** Practice mode stops flipping pages on tap and instead
  waits for me to play. When I've played enough of the right pitch classes in
  the current window (octave doesn't matter, so I can transpose if my hands
  prefer it), the page turns by itself.
- **Scoring.** Each note name in the measure gets a tick mark as I play its
  letter, and the info line counts hits and, when I rush, misses. The
  feedback is deliberately plain text and ticks rather than colored
  highlights — anything that depends on me telling colors apart is a dead
  end.

It only works over Chrome right now; Firefox on Android still ships Web MIDI
unreliably, and the app leans on it heavily.

## How it works

The entire app is one HTML file plus a vendored copy of the abcjs library. No
build step, no package manager, no framework. Deploying is copying files into
a folder.

```
app/              the app HTML, the vendored abcjs, and a local soundfont
files/            the ABC library (gitignored — content is copyrighted)
nginx/            nginx config: static server + JSON index for files/
specs/            written specs for the practice features
.specify/         spec-kit tooling used for spec work
```

### The fitting engine

abcjs computes layout in ways that shift between browsers and between zoom
levels, and fighting that model directly broke the layout three separate
times. The fitting engine sidesteps it entirely:

1. Render at scale 1 into a large internal canvas.
2. Stamp the note-name labels inside the same SVG.
3. Read the ink's bounding box with `getBBox()`.
4. Set that box as the SVG's `viewBox` and let `preserveAspectRatio="meet"`
   scale it into a flex container that fills the screen.

`preserveAspectRatio="meet"` contains the drawing by construction, so nothing
can fall off the edge — in landscape, in portrait, or when the browser sizes
things invasively. The notes fill the available width on every screen,
because that is the axis the viewBox gives them.

### Practice mode and fragments

Practice mode slices the ABC file into windows through `% bar N` comments —
every bar in the file carries one, which is a hard requirement for anything
that goes into my library. The fragment builder derives the musical header
(meter, unit length, tempo, key) from the actual file, so a 12/8 piece and a
4/4 piece both work without hardcoding. All bars inside a window join onto a
single music line — because abcjs interprets each new source line as a new
system, which produced stacked one-bar systems before I learned why — and a
mid-window key change is allowed to break the line where it belongs.

Note names do not come from the ABC text but from abcjs's parse result, using
the same order the renderer uses visually. An explicit accidental wins, then
the last accidental on that letter in the bar, then the key signature. The
labels live inside the SVG's own box, which keeps them from being clipped —
something mobile browsers do aggressively where desktop browsers happily
overflow.

### Playback and the piano

abcjs synthesizes from parse data, so the page hands fragments directly to
`CreateSynth` with a locally served grand piano. When a MIDI input is
connected, the app listens on it, tracks pitch classes, and — in duet mode —
synthesizes the opposite staff from a hidden render of the same fragment, so
the accompaniment is always exactly the music on screen.

### The transcription pipeline

The score comes from somewhere other than the app. PDFs arrive as either
vector exports (from Sibelius, MuseScore, and similar engravers) or scanned
images. Vector PDFs are decoded through the engraver's own font glyph table,
which is far more accurate than pixels. Scans go through a pixel-level
notehead pipeline. Either way, the result gets a second opinion from
Audiveris running in Docker — I compare note events per bar between the two
transcriptions and treat disagreements as flags to verify by hand. Then
`abc2midi` validates the rhythm end to end, the bar comments go in, and the
file lands in `files/`.

## Deployment

Everything runs as static files behind a reverse proxy. In my setup Caddy
terminates TLS and routes the subdomain, an oauth2-proxy sidecar fronts the
site with SSO (my sheet music isn't public), and an nginx container serves the
app and the JSON index of `files/`. Two non-obvious deployment requirements:
serve everything with `Cache-Control: no-store`, because I push code live and
a cached page will happily show a build from three edits ago; and serve
`/files/` as JSON autoindex, because the page builds its file list from it.

## Development notes

I test with headless Chromium and Firefox through Playwright at the real
viewport of my tablet — not only at desktop size, because mobile browsers
clip SVG content that desktop browsers overflow, and a desktop-only green
check proves nothing. A small build marker in the UI tells me which build the
browser is actually running, which has settled more than one argument about
stale caches.

The specifications in `specs/` record the design decisions and the reasoning
behind them: window paging, the fitting engine, the fragment builder, and the
size model.

## Status and roadmap

Working: score viewing, note names, 1-to-3 measure practice paging, synced
per-measure playback, whole-score playback, drag panning, themes, piano link
with duet, auto-advance, and scoring.

Still on the list:

- Polishing zoom inside practice mode.
- A tempo-following mode with time-aligned expected-note tracking.
- Bluetooth MIDI as a second transport.

## Copyright

The code is mine and MIT licensed. The ABC files in `files/` are generally
arrangements of copyrighted popular music, so they live in the mounted folder
on my server and stay out of git. The soundfont in `app/sf/` comes from the
FluidR3_GM set distributed by paulrosen/midi-js-soundfonts.
