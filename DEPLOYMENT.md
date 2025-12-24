# Deployment Guide

This guide covers deploying image-drift-generator to production environments.

## Prerequisites

- Python 3.9+
- FFmpeg installed and in PATH
- Sufficient disk space for frame storage (varies with resolution and duration)
- ~2GB+ RAM available (for processing high-resolution images)

## Local Deployment

### 1. System Setup

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg

# macOS with Homebrew
brew install python@3.11 ffmpeg

# Verify installations
python3 --version
ffmpeg -version
```

### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/VidiVici98/image-drift-generator.git
cd image-drift-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Edit `config.sh` with production settings:

```bash
# Set input image path
INPUT_IMAGE="input/your-image.png"

# Set output paths (use absolute paths for clarity)
OUTPUT_DIR="/var/cache/image-drift-generator"
FRAMES_DIR="/var/cache/image-drift-generator/frames"
FINAL_DIR="/var/cache/image-drift-generator/final"

# Optimize for your use case
OUT_W=1920
OUT_H=1080
DURATION_SECONDS=30
FPS=30
```

### 4. Running

```bash
# Generate preview
bash run.sh --preview

# Full generation
bash run.sh

# Check output
ls -lh output/final/
```

## Docker Deployment

### Building the Container

```bash
# Build image
docker build -t image-drift-generator:1.0 .

# Verify build
docker images | grep image-drift-generator
```

### Running the Container

```bash
# Basic run with volume mounts
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config.sh:/app/config.sh \
  image-drift-generator:1.0

# With environment variable override
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -e LOG_LEVEL=DEBUG \
  image-drift-generator:1.0
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  generator:
    build: .
    image: image-drift-generator:1.0
    container_name: image-drift-gen
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./config.sh:/app/config.sh
    environment:
      - LOG_LEVEL=INFO
      - FPS=30
    working_dir: /app
    restart: on-failure
```

Then run:

```bash
docker-compose up
```

## Kubernetes Deployment

### Create ConfigMap

```bash
kubectl create configmap image-drift-config \
  --from-file=config.sh=./config.sh
```

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-drift-generator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: image-drift-generator
  template:
    metadata:
      labels:
        app: image-drift-generator
    spec:
      containers:
      - name: generator
        image: image-drift-generator:1.0
        imagePullPolicy: IfNotPresent
        volumeMounts:
        - name: input
          mountPath: /app/input
        - name: output
          mountPath: /app/output
        - name: config
          mountPath: /app/config.sh
          subPath: config.sh
        env:
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
      volumes:
      - name: input
        persistentVolumeClaim:
          claimName: image-drift-input
      - name: output
        persistentVolumeClaim:
          claimName: image-drift-output
      - name: config
        configMap:
          name: image-drift-config
```

## Performance Optimization

### Memory Usage

For large images or long animations:

```bash
# Reduce frame size to lower memory
OUT_W=960
OUT_H=540

# Or reduce duration
DURATION_SECONDS=15
FPS=24

# Use less memory with smaller input
TARGET_PIXEL_WIDTH=400
```

### Storage Optimization

```bash
# Monitor disk usage during generation
watch -n 1 du -sh output/frames/

# Clean up intermediate frames after encoding
rm -rf output/frames/

# Archive final output
tar -czf animations-$(date +%Y%m%d).tar.gz output/final/
```

### CPU Optimization

Frame generation is CPU-bound. For faster processing:

```bash
# Use fewer frames for testing
FPS=15
TOTAL_FRAMES=$((DURATION_SECONDS * FPS))

# Parallel processing (if implemented)
# Currently single-threaded; consider batching for multiple animations
```

## Monitoring

### Health Checks

```bash
# Test generator
python3 -c "from src import generate_frames; generate_frames.validate_config()"

# Verify FFmpeg
ffmpeg -codecs | grep vp9
```

### Logging

```bash
# Enable debug logging
LOG_LEVEL=DEBUG bash run.sh

# Save logs to file
bash run.sh 2>&1 | tee generation.log
```

### Metrics to Monitor

- Disk usage (frames + output)
- Memory consumption during generation
- Processing time per frame
- FFmpeg encoding success rate

## Troubleshooting

### High Memory Usage

```bash
# Reduce canvas size
OUT_W=1280
OUT_H=720

# Generate in batches instead of one long animation
DURATION_SECONDS=10  # Instead of 60

# Monitor actual memory usage
ps aux | grep python | grep generate_frames
```

### Slow Processing

```bash
# Check CPU usage
htop -p $(pgrep -f generate_frames)

# Optimize input image size
TARGET_PIXEL_WIDTH=600  # Smaller = faster

# Use faster motion mode
MOTION_MODE=sine  # vs. perlin (slightly faster)
```

### FFmpeg Errors

```bash
# Verify FFmpeg installation
ffmpeg -version

# Check output directory
ls -la output/final/

# Try encoding manually
cd output/frames/
ffmpeg -framerate 30 -i testframe_%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 output.webm
```

## Backup and Recovery

### Backup Configuration

```bash
# Backup config files
cp config.sh config.sh.backup-$(date +%Y%m%d)

# Version control for configs
git add config.sh
git commit -m "Production config for video-v1"
```

### Recovery Procedure

1. Restore `config.sh` from backup
2. Verify input image exists
3. Clear `output/frames` directory
4. Re-run generation: `bash run.sh`

## Security Considerations

### File Permissions

```bash
# Create dedicated directory
sudo mkdir -p /var/cache/image-drift-generator
sudo chown user:user /var/cache/image-drift-generator
sudo chmod 755 /var/cache/image-drift-generator

# Restrict access
sudo chmod 700 /var/cache/image-drift-generator/final
```

### Input Validation

The application validates:

- Configuration parameter ranges
- Image file existence and readability
- Canvas dimensions are positive
- Motion modes are known

### Environment Isolation

In Docker, the application runs as non-root `appuser` (UID 1000).

## Updates and Patches

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update to latest compatible versions
pip install -U -r requirements.txt

# Verify functionality after update
make test
```

### Application Updates

```bash
# Pull latest version
git pull origin main

# Reinstall if dependencies changed
pip install -r requirements.txt

# Run tests
make test

# Deploy
bash run.sh
```

## Production Checklist

- [ ] Configuration reviewed and optimized
- [ ] Input images tested and validated
- [ ] Output directories created with proper permissions
- [ ] FFmpeg installed and tested
- [ ] Monitoring and logging configured
- [ ] Backup procedures documented
- [ ] Security settings reviewed
- [ ] Tests passing in production environment
- [ ] Documentation accessible to operations team
- [ ] Runbooks created for common tasks
