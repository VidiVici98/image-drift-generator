# Quick Reference

## Common Commands

```bash
# Setup & Install
make setup          # Create virtual environment
make install        # Install dependencies

# Development
make test           # Run tests with coverage
make lint           # Run flake8 linter
make format         # Auto-format code (black, isort)
make type-check     # Run mypy type checker

# Pre-commit
make pre-commit-install   # Install git hooks
make pre-commit-run       # Run checks manually

# Running
make preview        # Generate static preview
make run            # Full pipeline (generate + encode)
make clean          # Clean build artifacts

# Docker
make docker-build   # Build Docker image
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output image-drift-generator
```

## Configuration Quick Reference

Edit `config.sh`:

```bash
# Image input/output
INPUT_IMAGE="input/logo.png"
OUTPUT_DIR="output"
BASENAME="animation"

# Canvas size
OUT_W=1920
OUT_H=1080

# Timing
DURATION_SECONDS=30
FPS=30

# Image scaling
TARGET_PIXEL_WIDTH=600    # OR
SCALE=0.8

# Positioning
BASE_POS_MODE="center"    # OR "coords"
BASE_CENTER_OFFSET_X=0
BASE_CENTER_OFFSET_Y=0

# Motion
MOTION_MODE="perlin"      # OR "sine"
AMP_X=100
AMP_Y=50
NOISE_TIMESCALE_SECONDS=10    # For perlin
NOISE_SEED="12345"            # OR empty for random

# For sine mode
SINE_CYCLES_X=1.0
SINE_CYCLES_Y=1.0
```

## Environment Variables

```bash
# Override config without editing file
INPUT_IMAGE="other.png" DURATION_SECONDS=15 bash run.sh

# Logging
LOG_LEVEL=DEBUG make run          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO bash run.sh
```

## File Structure

```
input/                    # Put source images here
output/
  frames/                 # Generated PNG sequence
  final/                  # Encoded WebM output
src/
  generate_frames.py      # Main generator
  encode_webm.py          # Encoder
  errors.py               # Custom exceptions
  logging_config.py       # Logging setup
tests/                    # Unit tests
docs/
  USAGE.md                # Detailed usage
  CONFIGURATION.md        # Config reference
config.sh                 # Main configuration
Dockerfile                # Container definition
```

## Testing

```bash
# All tests
make test

# Specific test class
pytest tests/test_generation.py::TestConfigValidation -v

# With coverage report
pytest --cov=src --cov-report=html tests/

# Run during development
pytest tests/ -v --tb=short
```

## Docker

```bash
# Build
docker build -t image-drift-generator .

# Run with volumes
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config.sh:/app/config.sh \
  image-drift-generator

# With docker-compose
docker-compose up
```

## Documentation Files

- `README.md` - Project overview
- `docs/USAGE.md` - Complete usage guide with examples
- `docs/CONFIGURATION.md` - All configuration options explained
- `CONTRIBUTING.md` - Development guidelines
- `DEPLOYMENT.md` - Production deployment guide
- `SECURITY.md` - Security policy
- `IMPROVEMENTS.md` - Summary of improvements made
- `IMPROVEMENTS.md` - This quick reference

## Troubleshooting

```bash
# Check configuration
python3 -c "from src import generate_frames; generate_frames.validate_config()"

# Verify FFmpeg
ffmpeg -version

# Debug logging
LOG_LEVEL=DEBUG make preview

# Check disk usage
du -sh output/frames/

# Monitor memory during generation
watch -n 1 'ps aux | grep generate_frames'

# Clean up frames
rm -rf output/frames/*
```

## Performance Tips

```bash
# Fast preview (low resolution)
OUT_W=640 OUT_H=480 FPS=15 DURATION_SECONDS=5 make preview

# High quality (slow)
OUT_W=3840 OUT_H=2160 FPS=60 DURATION_SECONDS=60 make run

# Memory efficient
TARGET_PIXEL_WIDTH=400 DURATION_SECONDS=10 make run
```

## Getting Help

1. Check `docs/USAGE.md` for usage examples
2. See `docs/CONFIGURATION.md` for config options
3. Read `CONTRIBUTING.md` for development questions
4. Review `DEPLOYMENT.md` for production setup
5. Check `SECURITY.md` for security topics
6. Open an issue on GitHub for bugs/features
