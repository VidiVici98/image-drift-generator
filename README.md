
# image-drift-generator

Generate smooth drifting image animations (PNG frame sequences) and encode to VP9 WebM with alpha support.

## Features

- Lightweight Python scripts for frame generation and WebM encoding
- Two motion modes: Perlin noise or sine waves
- Full alpha channel support for transparent backgrounds
- Deterministic generation with configurable random seeds
- Type hints and comprehensive error handling
- Production-ready with Docker support, tests, and CI/CD
- Configurable via simple `config.sh` file
- Progress bars and detailed logging

## Quick Start

### 1. Setup

```bash
make setup
make install
```

### 2. Preview (Generate Static Image)

```bash
make preview
# Output: output/{BASENAME}_preview.png
```

### 3. Full Pipeline (Generate + Encode)

```bash
make run
# Outputs: PNG frames in output/frames/ and WebM in output/final/
```

## Files & Structure

```
image-drift-generator/
├── src/                    # Core Python modules
│   ├── generate_frames.py # Frame generation
│   ├── encode_webm.py     # WebM encoding
│   ├── errors.py          # Custom exceptions
│   └── logging_config.py  # Logging setup
├── tests/                 # Comprehensive test suite
├── docs/
│   ├── USAGE.md          # Detailed usage guide
│   └── CONFIGURATION.md  # Configuration reference
├── config.sh              # Main configuration file
├── run.sh                 # Pipeline wrapper
├── Dockerfile             # Container image
├── Makefile               # Development tasks
└── requirements.txt       # Python dependencies
```

## Configuration

Edit `config.sh` to customize output. Key parameters:

```bash
INPUT_IMAGE="input/logo.png"          # Source image
OUT_W=1920                              # Canvas width
OUT_H=1080                              # Canvas height  
DURATION_SECONDS=30                     # Animation length
FPS=30                                  # Frames per second
MOTION_MODE="perlin"                    # "perlin" or "sine"
AMP_X=100 AMP_Y=50                      # Motion amplitude
TARGET_PIXEL_WIDTH=600                  # Image scale
```

For complete documentation, see [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Usage Examples

### Docker
```bash
docker build -t image-drift-generator .
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output image-drift-generator
```

### Advanced Logging
```bash
LOG_LEVEL=DEBUG make run
```

### Direct Python
```python
from src import generate_frames, encode_webm
generate_frames.generate_frames(preview_only=False)
exit_code = encode_webm.main()
```

For more examples, see [docs/USAGE.md](docs/USAGE.md).

## Development

### Testing
```bash
make test              # Run tests
make lint              # Run linters
make format            # Auto-format code
make type-check        # Type checking with mypy
```

### Pre-commit Hooks
```bash
make pre-commit-install
make pre-commit-run
```

For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Deployment

For production deployment, containerization, and monitoring, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Requirements

- Python 3.9+
- FFmpeg (for WebM encoding)
- 2GB+ RAM (depending on resolution)

Runtime dependencies:
- Pillow (image processing)
- numpy (numerical computing)
- OpenSimplex (noise generation)
- tqdm (progress bars)

## Documentation

- [USAGE.md](docs/USAGE.md) - Detailed usage guide with examples
- [CONFIGURATION.md](docs/CONFIGURATION.md) - All configuration options
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development & contribution guidelines
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [SECURITY.md](SECURITY.md) - Security policy & best practices

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

To report security vulnerabilities, please see [SECURITY.md](SECURITY.md).
