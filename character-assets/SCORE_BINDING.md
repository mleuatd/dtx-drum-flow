# Score / Character Animation Binding

DTX Drum Flow can choose a character layer from chart timing, or a chart can explicitly request one.

## Automatic mode

For each note or simultaneous-note group:

1. Identify part(s).
2. Estimate local subdivision from BPM and neighboring notes.
3. Resolve quarter / eighth / sixteenth behavior.
4. For repeated sixteenth hits, alternate hands using the configured sticking sequence.
5. Resolve a simultaneous-hit rule when matching notes occur within the configured window.
6. Select character pose and phase.
7. Composite it over the immutable drum layer.

## Explicit JSON note metadata

A chart JSON note can override automatic selection:

```json
{
  "time": 5.755,
  "part": "HH",
  "velocity": 0.8,
  "animation": {
    "rule": "hh.sixteenth.alternate",
    "hand": "L",
    "phase": "hit"
  }
}
```

A fully locked frame can also be requested:

```json
{
  "time": 5.755,
  "part": "HH",
  "animation": {
    "frame": "hh/hit_l",
    "lockFrame": true
  }
}
```

## DTX / GDA / MIDI

These formats do not need custom animation metadata. Runtime mapping uses part + timing + neighboring notes.

When exact sticking is important, convert/export to DTX Drum Flow JSON and add the optional `animation` object.

## Sixteenth hi-hat default

Repeated HH sixteenths alternate:

`R L R L`

Quarter and eighth HH default to one hand.
