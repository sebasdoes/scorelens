# Scorelens

A self-hosted web viewer for ABC sheet music. I built it because I read music
slowly and I wanted a faster way to study piano pieces on a tablet.

The project lives in one page. It shows a score big, puts a letter with the
note name under every note head, plays the music, and can follow you while you
play a real piano.

## Why I started this project

I have achromatopsia. I see fine detail poorly, and color is no help to me.
Standard sheet music on a tablet is small. I can read it, but not quickly.

So I gave myself a short list of needs:

- Show one measure at a time. Fill the screen with it.
- Put the note name under each note head. This turns each measure into text
  that I can read fast.
- Play the measure, so I can compare what I hear with what I see.
- Work on my tablet in the browser. No app store. No install.

The first score I used for this was a piano arrangement of Hitchcock by
Yorushika. I transcribed it to ABC by hand and machine, with a second opinion
from an open-source OMR tool. Two more pieces followed. Now I add a PDF, I get
an ABC file, and I practice.

## Features

Main page:

- Lists the `.abc` files in a mounted folder. The loaded file gets a tick mark
  in the list.
- Draws the full score. It fills the screen width on any device.
- "Note names" toggle. This is the ♪A switch. It stamps the letter and the
  accidental below each note head.
- A zoom control for the whole score.
- Play. The browser synthesizes the piano sound. No MP3 files. No external
  CDN. The soundfont sits next to the page.
- Three themes: White, Dark, and High contrast (pure black with white notes).
  The choice persists.

Practice mode:

- Full screen. One, two, or three measures per window. You pick with the
  "Bars" slider.
- The measure fills the screen. Notes cannot fall off the edge, in landscape
  or portrait.
- Tap left to go back, tap right to go forward. Drag to pan.
- Voice toggle: RH, LH, or BOTH. RH and LH show one staff. BOTH shows one
  aligned grand staff.
- The info line shows the song title and your position.

Piano link (Web MIDI):

- Connect a class-compliant digital piano to the tablet with an OTG cable.
  I use a Yamaha P-105.
- With the piano connected, the play button becomes an accompanist. It plays
  the staff you are not reading, while you play the other one on the real
  piano.
- Auto-advance: the practice window waits for you and turns the page when you
  have played its pitch classes. Octave errors do not count against you.
- Scoring: a tick appears at each note name you played, the info line counts
  hits and misses. All feedback is text and ticks. I do not use color for
  information, because I cannot use color.

## The ABC file format

Scorelens needs each bar on its own lines. A file looks like this:

```
X:1
T:Time Flows Ever Onward
M:3/4
L:1/8
Q:1/4=114
K:C
%%score { 1 | 2 }
V:1 treble
V:2 bass
% bar 1
[V:1] C3 B, A,2|
[V:2] [A,,E,A,]6|
% bar 2
[V:1] ^G,6|
[V:2] [E,,B,,E,]6|
```

Rules that matter:

- Every bar starts with a `% bar N` comment. Practice mode splits the file on
  these comments. Without them, practice mode does not page.
- Blank lines end a tune for the ABC parser, silently. Keep the body
  continuous.
- Music lines carry the `[V:1]` or `[V:2]` voice tag.
- Key changes go inline as `[K:G]` lines between bars.

## Architecture

The whole app is one HTML file with the vendored abcjs library next to it.
I keep it that way on purpose. One file, no build step, no framework, no
package manager. I deploy by copying the file.

Layout of this folder:

```
app/
  index.html            the app
  abcjs-basic-min.js    abcjs 6.7.2, vendored
  sf/                   FluidR3 grand piano soundfont, served locally
files/                  the ABC library (ignored by git; content is personal)
nginx/                  nginx config for the static server and /files/ JSON
specs/                  written specifications for the practice features
.specify/               spec-kit tooling used for spec work
```

### The fitting engine

abcjs computes layout sizes in ways that shift between browsers and scales.
Fights with that model broke three builds. The current engine does not fight
it:

1. Render at scale 1 into a large internal canvas.
2. Stamp the note-name labels inside the same SVG.
3. Read the ink bounding box with `getBBox()`.
4. Set that box as the SVG `viewBox`, and let `preserveAspectRatio` scale it
   into a flex box that fills the screen.

`preserveAspectRatio` with "meet" always contains the drawing. Nothing can
clip, in any orientation. The notes fill the width on any screen. This one
pattern fixed every size bug I had: mobile clipping, wrong widths, and the
scale-versus-staffwidth confusion.

### Practice mode

A slice of the ABC file becomes a small fragment. The builder derives the
header (meter, unit length, tempo, key) from the file, so a 12/8 piece and a
4/4 piece both work. It joins all bars of the window into one music line,
because abcjs starts a new system for each source line. A key change inside
the window breaks the line, because a key change must sit at the start of a
line.

Note names are not parsed from the music text. They come from the parse
result of abcjs, with three rules: an explicit accidental wins, then the last
accidental on that letter in the bar, then the key signature. The label lane
sits under the staff, inside the SVG box, so mobile browsers do not clip it.

### Playback and the piano link

abcjs also synthesizes. The page renders fragments and hands them to
`CreateSynth` with a locally served grand piano soundfont. The browser loads
only the notes it needs.

When a MIDI device is connected, three things turn on:

- Duet. The play button plays the opposite staff from the one you read.
- Follow. The app listens on the MIDI input and matches pitch classes. This
  ignores octaves, so the same letter in another octave still counts.
- Auto-advance. After you play every pitch class of the window, the page
  turns.

Note requirements come from the same parse result, so the piano link and the
display always agree.

### Transcription pipeline

A printed PDF is not the input to the app. Someone (me, or an agent I task
with) converts it first:

1. If the PDF is vector, extract the music glyphs with their positions. Map
   the engraver font. Sibelius and MuseScore exports both work this way.
2. If the PDF is a scan, decode note heads from pixels. This is slower.
3. Get a second opinion from Audiveris in Docker. Compare note events
   per bar. Trust neither source; cross-check.
4. Validate with `abc2midi`, then add the `% bar N` comments and place the
   file in `files/`.

The accuracy check stays with the human. These files are arrangements with
rights, so I keep them out of the repository.

## Deployment

The stack is static files behind a reverse proxy. My deployment has three
parts: Caddy terminates TLS and gives one site per subdomain. An
oauth2-proxy sidecar fronts the site with SSO. An nginx container serves the
app and the JSON file index.

Requirements for a clean deployment:

- Serve everything with `Cache-Control: no-store`. I edit code live, and a
  cached page shows an old build.
- Serve `/files/` as JSON autoindex. The page filters and sorts.
- Put the soundfont in `app/sf/`, because `CreateSynth` loads notes from it
  at play time.

## Development notes

I test with headless Chromium and Firefox through Playwright, at the real
viewport of my tablet, not only at desktop size. Mobile browsers clip SVG
content that desktop browsers overflow, so a desktop-only check proves
nothing. A build marker in the UI tells me which build the browser shows.

Specifications for the practice features are in `specs/`. They record the
decisions I argued with myself about: window paging, the fitting engine, the
fragment builder, and the size model.

## Status and roadmap

Working: score viewing, note names, practice paging with 1 to 3 measures,
per-measure playback, whole-score playback, themes, drag panning, piano link
with duet, auto-advance, and scoring.

Wanted:

- Zoom polish inside practice mode.
- A tempo-controlled follow mode, with expected-note tracking in time.
- Bluetooth MIDI as a second transport.

## Copyright

The code in this repository is mine, and I share it under the MIT license.
The ABC files in `files/` are arrangements of copyrighted music. They stay
out of git, in the mounted folder only. The soundfont in `app/sf/` comes from
the FluidR3_GM set distributed in paulrosen/midi-js-soundfonts.
