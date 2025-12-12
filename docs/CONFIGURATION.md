# Configuration (`config.sh`)

This document explains every variable in `config.sh` and recommended values.

Edit `config.sh` to tune behavior; `run.sh` sources and exports the uppercase
variables so the Python scripts read them via the environment.

## Input / Output
- `INPUT_IMAGE` (string): Path to the source image relative to the repo root.
  - Must be a format supported by Pillow (PNG, JPG, WEBP, etc.). Use an image
    with an alpha channel (PNG/WEBP) if you want transparent output.
  - Example: `input/logo.png` or `input/logo.webp`.

- `OUTPUT_DIR` (string): Base output directory. Defaults to `output`.
- `BASENAME` (string): Base filename used for frames and final output.
  - Frames are named like `{BASENAME}_0001.png` and final file is
    `{BASENAME}.webm`.
- `FRAMES_DIR`, `FINAL_DIR` (strings): Derived from `OUTPUT_DIR` by default.

## Canvas / Size
- `OUT_W`, `OUT_H` (integers): Output canvas width and height in pixels.
  - Default: a portrait 1080x1920 canvas. Change to suit your target display.

## Timing
- `DURATION_SECONDS` (float): Duration of the generated animation in seconds.
- `FPS` (int): Frames per second.
- `TOTAL_FRAMES` (int): Total frames generated. By default set as
  `DURATION_SECONDS * FPS` in `config.sh`, but you may override it if needed.

## Image scaling
You can control how the input image is scaled onto the canvas using two
options — prefer `TARGET_PIXEL_WIDTH` when you need an exact width, otherwise
use the `SCALE` multiplier.

- `TARGET_PIXEL_WIDTH` (int or empty): If set, the input image will be resized
  to this width (px) while preserving aspect ratio. Useful when you want a
  specific pixel size for the logo.
- `SCALE` (float): Fallback multiplier applied to the input image width when
  `TARGET_PIXEL_WIDTH` is empty. For example `SCALE=0.5` scales width to 50%.

Example: `TARGET_PIXEL_WIDTH=600` will rescale your input to 600px wide.

## Base position (where the image is pasted)
- `BASE_POS_MODE` (string): `"center"` or `"coords"`.
  - `center`: image is centered on the canvas; use `BASE_CENTER_OFFSET_X` and
    `BASE_CENTER_OFFSET_Y` to nudge it.
  - `coords`: image pasted with its top-left at `(BASE_X, BASE_Y)`.
- `BASE_CENTER_OFFSET_X`, `BASE_CENTER_OFFSET_Y` (ints): Offsets applied when
  in `center` mode.
- `BASE_X`, `BASE_Y` (ints): Coordinates used in `coords` mode.

## Motion parameters
- `MOTION_MODE` (string): `"perlin"` or `"sine"`.
  - `perlin` (default): uses OpenSimplex noise for smooth pseudo-random drift.
  - `sine`: uses deterministic sine wave motion based on `SINE_CYCLES_X/Y`.

- `AMP_X`, `AMP_Y` (numbers): Horizontal and vertical amplitudes in pixels.
  - Example: `AMP_X=75` and `AMP_Y=50` means motion offset up to ±75px and
    ±50px.

- `NOISE_TIMESCALE_SECONDS` (float): For `perlin` mode, larger values slow
  the drift (low frequency), smaller values speed it up.

- `NOISE_SEED` (string/int or empty): If empty, a random seed is generated
  each run. Set a numeric seed (e.g., `42`) for deterministic, reproducible
  output.

- `SINE_CYCLES_X`, `SINE_CYCLES_Y` (floats): Number of sine cycles across the
  full `DURATION_SECONDS` when `MOTION_MODE` is `sine`.

## ffmpeg / encoding
- `FFMPEG_BIN` (string): Command or full path to `ffmpeg`. If the binary is
  not available on the PATH, set this to the full `ffmpeg` executable path.

## Practical tips
- For testing, set `DURATION_SECONDS` to a small value (e.g., `1`) and `FPS`
  to `2` to generate only 2 frames quickly.
- To get reproducible results, set `NOISE_SEED` to a fixed integer and ensure
  `TOTAL_FRAMES` is deterministic.
- Keep large outputs out of version control — `.gitignore` already excludes the
  `output/` directory.

## Examples
- Minimal preview-only run (no encoding):

```bash
# edit config.sh as needed, then:
bash run.sh --preview
```

- Full run (generate frames + encode):

```bash
bash run.sh
```

If you plan to automate or run multiple configurations, create copies of
`config.sh` or write a small wrapper that sets environment variables before
calling `src/generate_frames.py`.

## Quick tuning guide (what to change and why)

This section gives practical guidance: what parameters to tweak for common
goals, and what increasing or decreasing each value does.

- Canvas / output size (`OUT_W`, `OUT_H`)
  - Increase: larger final images, more pixels preserved, longer encode times.
  - Decrease: smaller files, faster generation/encode, may blur fine details.

- Duration / FPS (`DURATION_SECONDS`, `FPS`, `TOTAL_FRAMES`)
  - Increase `DURATION_SECONDS` (or `TOTAL_FRAMES`) to make a longer animation.
  - Increase `FPS` to make motion smoother; requires more frames and larger
    output. For previews, use low FPS (1-5).

- Image scale (`TARGET_PIXEL_WIDTH`, `SCALE`)
  - `TARGET_PIXEL_WIDTH` sets a precise output width for the input image.
    Increasing this makes the pasted image larger on the canvas.
  - `SCALE` is a relative multiplier — increasing scales the image up.

- Motion amplitude (`AMP_X`, `AMP_Y`)
  - Controls how far the image drifts (in pixels).
  - Increase `AMP_X` or `AMP_Y` to make the motion more dramatic; decrease to
    keep the image mostly stationary.

- Motion style / smoothness (`MOTION_MODE`, `NOISE_TIMESCALE_SECONDS`, `SINE_CYCLES_*`)
  - `MOTION_MODE=perlin` (OpenSimplex) gives smooth, organic random drift.
    - `NOISE_TIMESCALE_SECONDS`: larger -> slower, long wandering; smaller ->
      quicker jitter-style motion.
  - `MOTION_MODE=sine` gives perfectly periodic motion. Use `SINE_CYCLES_X` and
    `SINE_CYCLES_Y` to control how many oscillations occur over the full
    duration.

- Reproducibility (`NOISE_SEED`)
  - Empty => random on every run; set an integer seed for identical output
    across runs. Useful for CI, preview generation, or reproducing an effect.

## Example presets

Create copies of `config.sh` or source one of the presets in `configs/` to
quickly try common configurations. Example presets are available in
`configs/` (mobile, story, quick-preview). These are intentionally small and
conservative so they run quickly.

## Tuning tips
- Start with a small preview: `DURATION_SECONDS=1`, `FPS=2`, use `--preview`.
- When iterating on motion, keep `NOISE_SEED` fixed so you compare apples-to-apples.
- If encoding fails on CI due to missing `ffmpeg`, run only frame generation in CI
  or install `ffmpeg` on the runner.
