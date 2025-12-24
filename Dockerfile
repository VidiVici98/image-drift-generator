# Multi-stage build for image-drift-generator
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Set environment for logging
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# Entry point
ENTRYPOINT ["python", "-m", "src.generate_frames"]
CMD []
