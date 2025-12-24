# Usage

This document covers common usage patterns beyond the quick start in `README.md`.

## Basic Setup

1) Configure `config.sh` to match your input and desired output. Important fields:
- `INPUT_IMAGE` — input image path under `input/`.
- `OUT_W`, `OUT_H` — canvas size in pixels.
- `MOTION_MODE` — "perlin" or "sine".
- `DURATION_SECONDS`, `FPS` — timing.

## Running Locally

### Preview Only (no encoding)

Generate a static preview image showing the image placement without animating frames:

```bash
bash run.sh --preview
# or via Makefile:
make preview
```

Output: `output/{BASENAME}_preview.png`

### Full Pipeline (generate frames + encode)

```bash
bash run.sh
# or via Makefile:
make run
```

Output: PNG frames in `output/frames/` and WebM in `output/final/{BASENAME}.webm`

## Using the Makefile

For a reproducible workflow:

```bash
make setup          # Create virtualenv
make install        # Install dependencies
make preview        # Generate preview
make run            # Full pipeline
make test           # Run unit tests
make lint           # Run linters (flake8)
make format         # Auto-format code (black, isort)
make clean          # Remove build artifacts
```

## Docker Usage

Build and run the generator in a container:

```bash
# Build the image
docker build -t image-drift-generator .

# Run with your config
docker run --rm -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config.sh:/app/config.sh \
  image-drift-generator
```

## Configuration Examples

### Example 1: Centered Logo with Perlin Drift

```bash
# In config.sh:
INPUT_IMAGE="input/logo.png"
OUT_W=1920
OUT_H=1080
DURATION_SECONDS=15
FPS=30
TARGET_PIXEL_WIDTH=400
BASE_POS_MODE="center"
MOTION_MODE="perlin"
AMP_X=100
AMP_Y=50
NOISE_TIMESCALE_SECONDS=10
```

### Example 2: Top-Left Corner with Sine Wave

```bash
# In config.sh:
INPUT_IMAGE="input/banner.webp"
OUT_W=1280
OUT_H=720
DURATION_SECONDS=30
FPS=60
TARGET_PIXEL_WIDTH=800
BASE_POS_MODE="coords"
BASE_X=50
BASE_Y=50
MOTION_MODE="sine"
AMP_X=150
AMP_Y=75
SINE_CYCLES_X=2
SINE_CYCLES_Y=1.5
```

### Example 3: Small Preview GIF

```bash
# In config.sh:
INPUT_IMAGE="input/icon.png"
OUT_W=512
OUT_H=512
DURATION_SECONDS=5
FPS=15
SCALE=0.8
BASE_POS_MODE="center"
MOTION_MODE="sine"
AMP_X=20
AMP_Y=20
```

## Environment Variables

The generator reads configuration from environment variables. All standard `config.sh` variables can be overridden:

```bash
# Override specific settings without editing config.sh
INPUT_IMAGE="other/image.png" \
FPS=60 \
bash run.sh
```

### Logging Control

Set the `LOG_LEVEL` environment variable to control verbosity:

```bash
LOG_LEVEL=DEBUG bash run.sh
# or
LOG_LEVEL=WARNING make preview
```

Valid levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## Troubleshooting

### FFmpeg Not Found

If ffmpeg is not installed on your system, the encoder will print the exact command to run elsewhere:

```
cd <frames_dir>
ffmpeg -framerate 30 -i <pattern> -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 <output.webm>
```

You can run this command on another machine with ffmpeg installed.

### Image File Format Not Supported

Ensure your input image is in a format Pillow supports (PNG, JPG, WEBP, etc.):

```bash
# Convert to PNG if needed
convert input/image.bmp input/image.png
```

### Configuration Validation Errors

The tool validates all configuration parameters on startup. Check the error message for what needs to be fixed:

```
Configuration validation failed:
  - OUT_W must be positive (got -100)
  - MOTION_MODE must be 'perlin' or 'sine' (got 'invalid')
```

### Generating Many Frames

For high-resolution or long animations, frame generation can be memory-intensive. To reduce memory usage:

- Reduce `OUT_W` and `OUT_H`
- Reduce `DURATION_SECONDS * FPS`
- Use a smaller `TARGET_PIXEL_WIDTH`

## Advanced: Running Tests

```bash
# Run all tests
make test

# Run specific test
python -m pytest tests/test_generation.py::TestConfigValidation -v

# Generate coverage report
python -m pytest --cov=src tests/
```

## Advanced: Direct Python Usage

You can import the generator modules directly in Python:

```python
from src import generate_frames, encode_webm
import os

# Set environment
os.environ['INPUT_IMAGE'] = 'input/logo.png'
os.environ['OUT_W'] = '1920'
os.environ['OUT_H'] = '1080'

# Generate frames
generate_frames.generate_frames(preview_only=False)

# Encode to WebM
exit_code = encode_webm.main()
```
