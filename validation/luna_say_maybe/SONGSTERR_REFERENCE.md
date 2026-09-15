# Luna Say Maybe — Songsterr reference reconstruction

Reference:
- Songsterr: Luna Say Maybe Drum Tab, song id 1089457
- Revision id: 3745733
- Artist: 初星学園
- Drum part id: 3
- BPM: 139
- Time signature: 4/4
- Measures: 150

Reconstruction result:
- Total drum notes: 2,158
- Global audio alignment offset: +1.693 s
- Segment best offsets: 1.699 / 1.696 / 1.690 / 1.693 / 1.687 s
- Maximum segment-to-segment drift: 12 ms

Part counts:
- SN: 659
- BD: 523
- HH: 629
- RC: 103
- RD: 105
- LT: 60
- FT: 42
- HT: 37

Method:
1. Fetch Songsterr page state payload.
2. Fetch the drum revision JSON from Songsterr's CDN.
3. Interpret drum fret values as GM percussion note numbers.
4. Reconstruct all note times from exact beat durations, including tuplets.
5. Align the complete chart against the original instrumental MP3 using frequency-band transient correlation.
6. Keep one global offset to preserve the reference chart's rhythmic structure.
7. Export DTX, MIDI and browser notes JSON.

Important:
- The final chart is reference-tab based, not audio-to-MIDI inference.
- The chart itself is kept in the shared Library rather than committed to the public repository.
- Browser DTX parsing supports the generated #OFFSET directive.
- MIDI export preserves truly simultaneous note-on events.
