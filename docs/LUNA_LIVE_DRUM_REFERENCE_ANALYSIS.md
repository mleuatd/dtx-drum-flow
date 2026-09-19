# Luna say maybe — live drum reference analysis

Updated: 2026-09-19

## Source handling

The user-provided `01 Luna say maybe.mp3` was inspected only as a tonal and dynamic reference. The repository does not contain the source recording, stems, isolated hits, or copied excerpts.

## Measured reference characteristics

- Duration inspected: approximately 267.18 seconds
- Working analysis rate: 22,050 Hz mono
- Detected percussive onset candidates: 814
- Percussive-component energy distribution:
  - 20–100 Hz: 18.76%
  - 100–250 Hz: 13.74%
  - 250–800 Hz: 24.92%
  - 800–2,500 Hz: 26.99%
  - 2,500–8,000 Hz: 14.56%
  - 8,000 Hz and above: 0.93%

These values are mix-level observations, not isolated drum measurements. Guitar, bass, vocals and mastering affect them, so they are used as directional constraints rather than exact reconstruction targets.

## Audible design targets

### Kick

- Strong low-frequency body instead of a short electronic click
- Fast beater attack around the upper midrange
- Controlled sub decay so dense passages remain clear
- Pitch drops rapidly after impact

### Snare

- Distinct shell/body and snare-wire layers
- Bright attack, but not dominated by white noise
- Short enough for the fast arrangement while retaining an acoustic tail
- Separate side-stick/cross-stick voice for GM note 37

### Toms

- Clearly descending HT → LT → FT pitch relationship
- Membrane attack followed by resonant shell/body decay
- Floor tom has the longest and heaviest decay
- Avoid pure sine-wave “poink” character by adding upper modes and stick noise

### Hi-hat

- Closed and open articulations must have clearly different decay lengths
- Metallic partials are intentionally inharmonic
- Closed hi-hat remains tight enough for repeated eighth/sixteenth notes

### Ride

- Defined ping plus controlled metallic wash
- Shorter and more focused than crash cymbals

### Crash cymbals

- Long broadband wash with multiple inharmonic modes
- Left and right cymbals use different partial sets
- Decay must overlap subsequent notes naturally rather than being cut off

### Live-room character

- Close-microphone signal stays dominant
- Two short early reflections create a compact live-room feel
- Room return is low-pass filtered so the mix does not become brittle
- Moderate bus compression glues simultaneous kick/snare/cymbal hits

## Implementation

The first reusable engine is implemented in:

- `site/live-drum-engine.js`

Preset:

- `Luna Live Kit v1`

The engine is procedural Web Audio synthesis and contains no copyrighted audio samples. It exposes separate kick, snare, side-stick, hi-hat, HT, LT, FT, ride, left crash and right crash voices, plus velocity humanization and a compact room bus.

## Next integration step

Replace the legacy inline `drumAt()` synthesis path in `site/app.js` with one `LiveDrumEngine` instance, while preserving:

- scheduler timing
- playback-speed behavior
- GM note 37 side-stick handling
- GM note 46 open-hi-hat handling
- part flash timing
- original-audio ON/OFF behavior

After integration, run JavaScript syntax validation, GitHub Pages deployment and browser playback QA on both PC and Xperia-sized viewports.
