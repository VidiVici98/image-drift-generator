# Usage

This document covers common usage patterns beyond the quick start in `README.md`.

1) Configure `config.sh` to match your input and desired output. Important fields:
- `INPUT_IMAGE` — input image path under `input/`.
- `OUT_W`, `OUT_H` — canvas size in pixels.
- `MOTION_MODE` — "perlin" or "sine".
- `DURATION_SECONDS`, `FPS` — timing.

2) Preview only (no frames encoded):

```bash
bash run.sh --preview
```

3) Full run (generate frames + encode to webm):

```bash
bash run.sh
```

4) Use `Makefile` targets for a reproducible developer workflow:
- `make setup` — create venv
- `make install` — install runtime + dev deps
- `make preview` — preview
- `make run` — full run

5) Troubleshooting:
- If `ffmpeg` is missing, the encoder will print the command to run on a system with `ffmpeg`.
- For CI, ensure `requirements-dev.txt` is installed so tests and linters run.
