
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
# image-drift-generator — Master Documentation

This `README.md` is the single authoritative source of information for the
project: usage, configuration, development, packaging, CI, and troubleshooting.

Table of contents
- Project overview
- Quick start
- File structure
- Configuration (quick reference)
- Presets and examples
- Tuning guide (what changes do)
- Development & tests
- Packaging & CLI
- CI
- Troubleshooting
- Contributing & license

Project overview
----------------
Generate smooth drifting animations from a single image and produce an
alpha-capable VP9 WebM. The pipeline is intentionally simple:

- `src/generate_frames.py` — generates PNG frames using OpenSimplex or sine
	motion.
- `src/encode_webm.py` — encodes frames to VP9 WebM via `ffmpeg`.
- `run.sh` — helper that sources `config.sh`, sets up a venv, runs generation
	and encoding.

Quick start
-----------
Recommended (Makefile-driven):

```bash
# create virtualenv and install runtime+dev deps
make setup
make install

# preview (fast, creates preview image only)
make preview

# full run (generate frames + encode)
make run
```

If you prefer direct commands:

```bash
bash run.sh --preview   # preview only
bash run.sh             # full pipeline
```

File structure (production-ready)
--------------------------------
- `src/` — Python package containing the generator and encoder
	- `src/generate_frames.py` — main frame generator (exports `main()`)
	- `src/encode_webm.py` — encoder (exports `main()`)
	- `src/logging_config.py`, `src/errors.py` — infra utilities
- `input/` — place source image(s) here (not tracked)
- `output/` — generated frames and final outputs (ignored by git)
	- `output/frames` — PNG sequence
	- `output/final` — WebM outputs
- `configs/` — preset config files for common output targets
- `docs/` — detailed docs (configuration reference, usage)
- `tests/` — unit and integration tests
- `Makefile` — local workflow helpers (`setup`, `install`, `test`, `preview`, `run`)
- `requirements.txt` + `requirements-dev.txt` — runtime and developer deps
- `pyproject.toml` — packaging and CLI entry points

Configuration — quick reference
--------------------------------
All variables are in `config.sh`. Key options:

- `INPUT_IMAGE`: path to input image (PNG/WEBP recommended for alpha)
- `OUTPUT_DIR`, `FRAMES_DIR`, `FINAL_DIR`: output directories
- Canvas: `OUT_W`, `OUT_H`
- Timing: `DURATION_SECONDS`, `FPS`, `TOTAL_FRAMES`
- Scaling: `TARGET_PIXEL_WIDTH` (preferred) or `SCALE`
- Position: `BASE_POS_MODE` (`center` or `coords`), `BASE_X/Y` or offsets
- Motion: `MOTION_MODE` (`perlin` or `sine`), `AMP_X`, `AMP_Y`
- Noise: `NOISE_TIMESCALE_SECONDS`, `NOISE_SEED`
- Encoder: `FFMPEG_BIN` (path to ffmpeg)

For a complete and annotated description, see `docs/CONFIGURATION.md`.

Presets and examples
---------------------
Presets are provided in the `configs/` directory as ready-to-source shell
files. Example presets:

- `configs/preset_preview.sh` — fast low-res preview
- `configs/preset_mobile.sh` — mobile wallpaper (1080x1920)
- `configs/preset_story.sh` — Instagram story style loop

Use a preset like this:

```bash
source configs/preset_preview.sh
bash run.sh --preview
```

You can also copy a preset into `config.sh` and tweak values.

Practical tuning guide
----------------------
Short guidance on how changing parameters affects results:

- `OUT_W`, `OUT_H`: increase to improve final resolution; larger files and
	longer encoding times.
- `DURATION_SECONDS` / `FPS`: increase `FPS` for smoother motion; increase
	`DURATION_SECONDS` to lengthen the animation. Both increase frame count.
- `TARGET_PIXEL_WIDTH` / `SCALE`: change the on-canvas size of the input image.
- `AMP_X`, `AMP_Y`: larger values produce more dramatic drift.
- `NOISE_TIMESCALE_SECONDS`: in `perlin` mode, larger -> slower motion;
	smaller -> faster jitter.
- `NOISE_SEED`: set to an integer for deterministic output; empty for random
	each run.

Development & testing
---------------------
Install development dependencies (from project root):

```bash
make setup
make install
```

Run linters and tests:

```bash
make lint
make test
```

Pre-commit hooks (recommended):

```bash
pre-commit install
pre-commit run --all-files
```

Tests are located in `tests/`. They are deterministic and use `tmp_path` and
`monkeypatch` fixtures to avoid touching real inputs/outputs.

Packaging & CLI
---------------
This project is pip-installable. `pyproject.toml` defines metadata and
console scripts:

- `image-drift-generate` → `src.generate_frames:main`
- `image-drift-encode` → `src.encode_webm:main`

Install locally for CLI usage:

```bash
python -m pip install --upgrade pip wheel setuptools
python -m pip install -e .
# now you can run:
image-drift-generate --preview
image-drift-encode
```

CI
--
GitHub Actions workflow `.github/workflows/python-app.yml` installs runtime
and dev dependencies, runs `flake8` and `pytest`. If you need encoding in CI,
ensure `ffmpeg` is available on the runner or split generation and encoding.

Troubleshooting
---------------
- `ffmpeg` missing: encoding step prints the exact `ffmpeg` command — run it
	on a machine with `ffmpeg` installed.
- Installation issues in CI: consider caching pip or pinning versions in
	`requirements-dev.txt`.

Contributing & License
----------------------
See `CONTRIBUTING.md` for contribution guidelines. The project is licensed
under the MIT License (see `LICENSE`).

Cleaning up redundant READMEs
-----------------------------
Small per-folder README files were removed and consolidated into this
master `README.md`. Use this file and `docs/CONFIGURATION.md` as your
primary documentation.

Contact
-------
Open issues or PRs on the repository to report bugs or propose features.

---

If you want, I can additionally:
- Add `configs/README.md` documenting each preset and explaining use-cases.
- Add a `scripts/use_preset.sh` wrapper that safely sources a preset and runs
	the pipeline.
- Convert `docs/` into an MkDocs site for publishing.

Feature checklist
-----------------
The project includes the following features (covered elsewhere in this
README and in `docs/`):

- Frame generation with two motion modes: `perlin` (OpenSimplex) and `sine`.
- Preview mode: `bash run.sh --preview` or `image-drift-generate --preview`.
- Deterministic runs with `NOISE_SEED` for reproducible output.
- Configurable scaling (`TARGET_PIXEL_WIDTH` or `SCALE`) and base position
  (`center` or explicit coordinates).
- Encoding to VP9 WebM with alpha via `ffmpeg` (configurable `FFMPEG_BIN`).
- Centralized logging (`LOG_LEVEL` env var) and structured error handling with
  clear exit codes.
- Packaging configured via `pyproject.toml` and console scripts
  (`image-drift-generate`, `image-drift-encode`).
- Developer tooling: `Makefile`, `requirements-dev.txt`, pre-commit hooks,
  flake8, black/isort, and unit tests under `tests/`.
- Preset configs in `configs/` for quick runs (preview, mobile, story).

Suggested next steps (prioritized)
---------------------------------
These are recommended actions to finish release readiness (ordered):

1. Run the test and lint pipeline locally and fix any issues:

```bash
make setup
make install
make lint
make test
```

2. Add example input images and expected outputs to `examples/` (do not
	commit large binaries; keep small samples for CI and docs). Update
	`configs/` presets to reference example images.

3. Verify GitHub Actions run cleanly on the first push. If encoding is not
	required in CI, keep tests unit-only; otherwise add an `ffmpeg` step to
	the workflow or separate generation and encoding.

4. Decide on a versioning strategy and release plan:
	- Update `pyproject.toml` `version` before publishing.
	- Tag releases in git (e.g., `v0.1.0`) and optionally publish to PyPI.

5. (Optional) Publish documentation as a site:
	- Convert `docs/` into an MkDocs site and add a GH Action to publish to
	  GitHub Pages.

6. Add integration tests (optional) that run a small generation+encode
	locally (use tiny presets) to validate end-to-end behavior.

7. Create a `configs/README.md` and/or `scripts/use_preset.sh` to make
	presets easy to discover and run (I can add these for you).

If you want, I can start with any of the above — run tests here, add
`configs/README.md`, or scaffold MkDocs and a publish workflow. Which
next step should I take? 

