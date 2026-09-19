# Acoustic Drum Engine — Luna reference rebuild

Status: IN_PROGRESS / sample-based acoustic engine active.

## Decision
The previous oscillator/noise procedural kit is not accepted as the target sound. Runtime now uses real acoustic multisamples derived from **Virtuosity Drums** via the ferrosintesis CC0 sample bank. The bank provides velocity layers and round robins; source/provenance is CC0. Luna say maybe is used only as a timbral and arrangement reference; no source recording is embedded or redistributed.

## Runtime voices
kick, snare, sideStick, hihatClosed, hihatOpen, hihatPedal, tomHigh, tomLow, tomFloor, ride, rideBell, crashLeft, crashRight.

Resolution remains explicit soundKey/drumVoice -> GM note -> part -> final fallback. Unknown notes remain audible and are diagnosable through soundResolution.

## Humanization
Velocity selects recorded layers. Repeated hits rotate recorded round-robin samples. Playback rate receives only a very small variation. Cymbal tails are independent AudioBufferSourceNodes and overlap naturally.

## Known limitation / next QA
The attached/reference mix is not stored in the repository and its exact isolated drum stems are unavailable, so spectral matching of isolated instruments is not claimed complete. Next QA is listening comparison in the public runtime and per-voice gain/EQ/tail tuning. The current change is a deliberate replacement of the rejected synthetic timbre, not a final claim of perfect Luna matching.

## Provenance
Upstream: 0x4D44/ferrosintesis, crates ferrosintesis-samples-drumkit and ferrosintesis-samples-drumkit2.
Upstream documentation identifies the prepared samples as Virtuosity Drums, CC0 1.0.
