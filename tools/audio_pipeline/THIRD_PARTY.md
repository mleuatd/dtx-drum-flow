# Third-party audio components

No third-party source code or model weights are vendored here.

The precision pipeline can invoke separately installed tools. Their licenses remain upstream licenses.

| Component | Purpose | License / note |
|---|---|---|
| Demucs | full-mix source separation | MIT |
| drumsep | split isolated drum stem into kick/snare/hihat/cymbals/toms | MIT |
| MDX23C wrappers/models | optional higher-quality drum separation | check upstream package and model license |
| ADTOF original | automatic drum transcription | CC BY-NC-SA 4.0; non-commercial restriction matters |
| ADTOF-pytorch / ADTOF Plus | optional transcription path | check upstream LICENSE and model-weight terms |

The default code in this repository does not redistribute any of those model weights.
