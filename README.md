
# image-drift-generator

Generate drifting image animations (PNG frame sequences) and encode to VP9 WebM with optional alpha.

Features
- Lightweight Python scripts in `src/` to generate frames and encode to WebM
- Configurable via `config.sh` (positioning, motion type, duration, canvas size)
- Dev tooling included: `Makefile`, `pyproject.toml`, `requirements-dev.txt`, pre-commit hooks

Quick start
1. Create a Python virtual environment and install dependencies (recommended):

```bash
make setup
make install
```

2. Create a preview image to validate configuration (no encoding):

```bash
make preview
# or: bash run.sh --preview
```

3. Run the full pipeline (generate frames, then encode):

```bash
make run
# or: bash run.sh
```

Files and layout
- `src/` — source scripts: `generate_frames.py`, `encode_webm.py`
- `config.sh` — configuration (edit values to control output)
- `run.sh` — wrapper that creates venv (if needed), exports config, runs generator and encoder
- `input/` — place your source image(s) here
- `output/frames` — generated PNG frames
- `output/final` — encoded WebM output

Configuration (quick reference)
- `INPUT_IMAGE` — path under `input/` to the source image (supports alpha)
- `OUT_W`, `OUT_H` — canvas width and height (px)
- `DURATION_SECONDS`, `FPS` — timing
- `MOTION_MODE` — `perlin` or `sine`
- `AMP_X`, `AMP_Y` — motion amplitudes in pixels
- `TARGET_PIXEL_WIDTH` or `SCALE` — scale the input image

The default `config.sh` contains comments explaining each option — edit it to tune your output. `run.sh` sources `config.sh` and exports the uppercase variables so `generate_frames.py` reads them via environment.

Encoder / ffmpeg
- The encoder uses `ffmpeg` to encode VP9 (`libvpx-vp9`) with alpha (`yuva420p`). Ensure `ffmpeg` is installed and on `PATH` before running the full pipeline.

Development & testing
- Run lint and tests after installing dev deps:

```bash
make lint
make test
```

- Install pre-commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```

CI
- A GitHub Actions workflow is provided at `.github/workflows/python-app.yml`. It installs runtime and dev dependencies, runs `flake8` and `pytest`.

Contributing
- See `CONTRIBUTING.md` for the contribution workflow. Keep changes small and add tests when possible.

License
- MIT (see `LICENSE`)

Contact
- Open issues or PRs on the repository to report bugs or propose features.

