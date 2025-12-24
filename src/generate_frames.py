#!/usr/bin/env python3
"""
generate_frames.py

Reads config from environment (run.sh exports config.sh values).
Usage:
  python generate_frames.py            # generate frames (PNG sequence)
  python generate_frames.py --preview  # generate only preview image and exit
"""

import os
import sys
import math
import random
from typing import Optional, Tuple
from PIL import Image, ImageDraw
import numpy as np
from opensimplex import OpenSimplex
from tqdm import tqdm

try:
    # preferred when the package is installed or imported as a package
    from .logging_config import setup_logger
    from .errors import ConfigError, GenerationError
except Exception:
    # fallback when running the script directly (python src/generate_frames.py)
    from logging_config import setup_logger
    from errors import ConfigError, GenerationError


logger = setup_logger(__name__)

# Helper: read env variables with defaults
def env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read environment variable with optional default value."""
    v = os.environ.get(name, None)
    if v is None:
        return default
    return v

# Load configuration from environment
INPUT_IMAGE = env("INPUT_IMAGE", "input/image.png")
OUTPUT_DIR = env("OUTPUT_DIR", "output")
FRAMES_DIR = env("FRAMES_DIR", os.path.join(OUTPUT_DIR, "frames"))
FINAL_DIR = env("FINAL_DIR", os.path.join(OUTPUT_DIR, "final"))
BASENAME = env("BASENAME", "testframe")

OUT_W = int(env("OUT_W", 1080))
OUT_H = int(env("OUT_H", 1920))

DURATION_SECONDS = float(env("DURATION_SECONDS", 30))
FPS = int(env("FPS", 30))
TOTAL_FRAMES = int(env("TOTAL_FRAMES", int(DURATION_SECONDS * FPS)))

TARGET_PIXEL_WIDTH = env("TARGET_PIXEL_WIDTH", "")
SCALE = float(env("SCALE", 0.65))

BASE_POS_MODE = env("BASE_POS_MODE", "center")
BASE_CENTER_OFFSET_X = int(env("BASE_CENTER_OFFSET_X", 0))
BASE_CENTER_OFFSET_Y = int(env("BASE_CENTER_OFFSET_Y", 0))
BASE_X = int(env("BASE_X", 100))
BASE_Y = int(env("BASE_Y", 200))

MOTION_MODE = env("MOTION_MODE", "perlin").lower()
AMP_X = float(env("AMP_X", 18))
AMP_Y = float(env("AMP_Y", 12))
NOISE_TIMESCALE_SECONDS = float(env("NOISE_TIMESCALE_SECONDS", 12.0))
NOISE_SEED = env("NOISE_SEED", "")
SINE_CYCLES_X = float(env("SINE_CYCLES_X", 0.6))
SINE_CYCLES_Y = float(env("SINE_CYCLES_Y", 0.5))

FFMPEG_BIN = env("FFMPEG_BIN", "ffmpeg")

# Derived
if TARGET_PIXEL_WIDTH is None:
    TARGET_PIXEL_WIDTH = ""
if TARGET_PIXEL_WIDTH != "":
    TARGET_PIXEL_WIDTH = int(TARGET_PIXEL_WIDTH)

# Validation helper
def validate_config() -> None:
    """Validate all configuration parameters.
    
    Raises:
        ConfigError: If any configuration is invalid.
    """
    errors = []
    
    if not INPUT_IMAGE:
        errors.append("INPUT_IMAGE not set")
    if OUT_W <= 0:
        errors.append(f"OUT_W must be positive (got {OUT_W})")
    if OUT_H <= 0:
        errors.append(f"OUT_H must be positive (got {OUT_H})")
    if DURATION_SECONDS <= 0:
        errors.append(f"DURATION_SECONDS must be positive (got {DURATION_SECONDS})")
    if FPS <= 0:
        errors.append(f"FPS must be positive (got {FPS})")
    if TOTAL_FRAMES <= 0:
        errors.append(f"TOTAL_FRAMES must be positive (got {TOTAL_FRAMES})")
    if SCALE <= 0:
        errors.append(f"SCALE must be positive (got {SCALE})")
    if TARGET_PIXEL_WIDTH and TARGET_PIXEL_WIDTH <= 0:
        errors.append(f"TARGET_PIXEL_WIDTH must be positive (got {TARGET_PIXEL_WIDTH})")
    if MOTION_MODE not in ("perlin", "sine"):
        errors.append(f"MOTION_MODE must be 'perlin' or 'sine' (got '{MOTION_MODE}')")
    if NOISE_TIMESCALE_SECONDS <= 0:
        errors.append(f"NOISE_TIMESCALE_SECONDS must be positive (got {NOISE_TIMESCALE_SECONDS})")
    if SINE_CYCLES_X < 0:
        errors.append(f"SINE_CYCLES_X must be non-negative (got {SINE_CYCLES_X})")
    if SINE_CYCLES_Y < 0:
        errors.append(f"SINE_CYCLES_Y must be non-negative (got {SINE_CYCLES_Y})")
    if BASE_POS_MODE not in ("center", "coords"):
        errors.append(f"BASE_POS_MODE must be 'center' or 'coords' (got '{BASE_POS_MODE}')")
    
    if errors:
        error_msg = "\n".join(f"  - {e}" for e in errors)
        raise ConfigError(f"Configuration validation failed:\n{error_msg}")

# Utility
def verbose_print(*a: any, **k: any) -> None:
    """Log informational messages (backward-compatible wrapper)."""
    logger.info("%s", " ".join(str(x) for x in a))

def ensure_dirs() -> None:
    """Create output directories if they don't exist."""
    try:
        os.makedirs(FRAMES_DIR, exist_ok=True)
        os.makedirs(FINAL_DIR, exist_ok=True)
    except OSError as e:
        raise GenerationError(f"Failed to create output directories: {e}") from e

def load_and_scale_image() -> Image.Image:
    """Load and scale the input image.
    
    Returns:
        Pillow Image object in RGBA mode.
        
    Raises:
        ConfigError: If input image not found or unsupported format.
        GenerationError: If image loading fails.
    """
    if not os.path.isfile(INPUT_IMAGE):
        raise ConfigError(f"Input image not found: {INPUT_IMAGE}")
    try:
        img = Image.open(INPUT_IMAGE).convert("RGBA")
    except Exception as e:
        raise ConfigError(f"Failed to load image {INPUT_IMAGE}: {e}") from e
    
    w0, h0 = img.size
    if TARGET_PIXEL_WIDTH:
        target_w = int(TARGET_PIXEL_WIDTH)
        scale = target_w / float(w0)
        target_h = int(round(h0 * scale))
        img = img.resize((target_w, target_h), resample=Image.LANCZOS)
    else:
        target_w = int(round(w0 * SCALE))
        target_h = int(round(h0 * SCALE))
        img = img.resize((target_w, target_h), resample=Image.LANCZOS)
    return img

def compute_base_position(img_w: int, img_h: int) -> Tuple[int, int]:
    """Compute the base position for pasting the image on the canvas.
    
    Args:
        img_w: Image width in pixels.
        img_h: Image height in pixels.
        
    Returns:
        Tuple of (x, y) coordinates.
    """
    if BASE_POS_MODE == "center":
        x = (OUT_W - img_w) // 2 + BASE_CENTER_OFFSET_X
        y = (OUT_H - img_h) // 2 + BASE_CENTER_OFFSET_Y
        return x, y
    else:
        return BASE_X, BASE_Y

def zero_pad_width(total: int) -> int:
    """Calculate zero-padding width needed for frame numbering."""
    return max(4, len(str(int(total))))

def build_preview(canvas_w: int, canvas_h: int, img: Image.Image, 
                  paste_xy: Tuple[int, int], outpath: str) -> None:
    """Build and save a preview image with checkerboard background.
    
    Args:
        canvas_w: Canvas width in pixels.
        canvas_h: Canvas height in pixels.
        img: Pillow Image object.
        paste_xy: Tuple of (x, y) for pasting the image.
        outpath: Output file path.
    """
    # checkerboard background
    cs = 16
    preview = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(preview)
    c1 = (220, 220, 220, 255)
    c2 = (180, 180, 180, 255)
    cols = math.ceil(canvas_w / cs)
    rows = math.ceil(canvas_h / cs)
    for y in range(rows):
        for x in range(cols):
            color = c1 if (x + y) % 2 == 0 else c2
            draw.rectangle([x*cs, y*cs, (x+1)*cs, (y+1)*cs], fill=color)
    preview.paste(img, paste_xy, img)
    preview.save(outpath)
    verbose_print("Preview written to:", outpath)

# Noise generator using OpenSimplex
def make_noise(seed: Optional[str] = None) -> Tuple[OpenSimplex, int]:
    """Create a noise generator with optional seeding.
    
    Args:
        seed: Optional seed value as string or int. If None or empty, uses random seed.
        
    Returns:
        Tuple of (OpenSimplex generator, used_seed_int).
    """
    if seed is None or seed == "":
        seed_int = random.randint(0, 2**30-1)
    else:
        try:
            seed_int = int(seed)
        except (ValueError, TypeError):
            seed_int = random.randint(0, 2**30-1)
    gen = OpenSimplex(seed_int)
    return gen, seed_int

def perlin_like_offsets(gen: OpenSimplex, t_seconds: float, amp_x: float, amp_y: float, 
                        timescale_seconds: float, seed_offset_x: float = 0.0, 
                        seed_offset_y: float = 0.0) -> Tuple[float, float]:
    """Generate perlin-like noise offsets for motion.
    
    Args:
        gen: OpenSimplex noise generator.
        t_seconds: Time in seconds.
        amp_x: X amplitude in pixels.
        amp_y: Y amplitude in pixels.
        timescale_seconds: Timescale for noise frequency.
        seed_offset_x: Seed offset for X coordinate.
        seed_offset_y: Seed offset for Y coordinate.
        
    Returns:
        Tuple of (dx, dy) offset values in pixels.
    """
    # produce offsets using opensimplex noise in an open domain
    # timescale_seconds maps to frequency (freq = 1/timescale)
    freq = 1.0 / max(1e-6, timescale_seconds)
    nx = gen.noise2d(t_seconds * freq + seed_offset_x, 0.0)
    ny = gen.noise2d(t_seconds * freq + seed_offset_y, 33.33)
    # noise output ~[-1,1]
    dx = nx * amp_x
    dy = ny * amp_y
    return dx, dy

def sine_offsets(t_seconds: float, duration: float, amp_x: float, amp_y: float, 
                 cycles_x: float, cycles_y: float) -> Tuple[float, float]:
    """Generate sine wave offsets for motion.
    
    Args:
        t_seconds: Time in seconds.
        duration: Total duration in seconds.
        amp_x: X amplitude in pixels.
        amp_y: Y amplitude in pixels.
        cycles_x: Number of cycles over duration for X.
        cycles_y: Number of cycles over duration for Y.
        
    Returns:
        Tuple of (dx, dy) offset values in pixels.
    """
    t_norm = t_seconds / max(1e-9, duration)
    dx = math.sin(2 * math.pi * (t_norm * cycles_x)) * amp_x
    dy = math.sin(2 * math.pi * (t_norm * cycles_y) + 1.7) * amp_y
    return dx, dy

def generate_frames(preview_only: bool = False) -> None:
    """Generate animation frames.
    
    Args:
        preview_only: If True, only generate preview and return.
        
    Raises:
        GenerationError: If frame generation fails.
    """
    # Validate configuration first
    try:
        validate_config()
    except ConfigError:
        raise
    
    try:
        ensure_dirs()
        img = load_and_scale_image()
    except Exception as e:
        logger.exception("Failed preparing generation environment")
        raise GenerationError("setup failed") from e
    img_w, img_h = img.size
    base_x, base_y = compute_base_position(img_w, img_h)
    logger.info("Canvas: %dx%d; image: %dx%d; base pos: (%d,%d)", OUT_W, OUT_H, img_w, img_h, base_x, base_y)
    preview_path = os.path.join(OUTPUT_DIR, f"{BASENAME}_preview.png")
    try:
        build_preview(OUT_W, OUT_H, img, (base_x, base_y), preview_path)
    except Exception as e:
        logger.exception("Failed building preview")
        raise GenerationError("preview failed") from e
    if preview_only:
        logger.info("Preview only requested; exiting.")
        return

    # prepare noise
    noise_gen, used_seed = make_noise(NOISE_SEED)
    logger.info("Using noise seed: %s", used_seed)

    pad = zero_pad_width(TOTAL_FRAMES)
    fname_template = f"{BASENAME}_{{:0{pad}d}}.png"

    logger.info("Generating %d frames...", TOTAL_FRAMES)
    for i in tqdm(range(TOTAL_FRAMES), desc="Generating frames", unit="frame"):
        t_seconds = i * (DURATION_SECONDS / max(1, TOTAL_FRAMES))
        if MOTION_MODE == "perlin":
            # simple decorrelated offsets
            dx, dy = perlin_like_offsets(noise_gen, t_seconds, AMP_X, AMP_Y, NOISE_TIMESCALE_SECONDS, seed_offset_x=0.0, seed_offset_y=100.0)
        else:
            dx, dy = sine_offsets(t_seconds, DURATION_SECONDS, AMP_X, AMP_Y, SINE_CYCLES_X, SINE_CYCLES_Y)
        paste_x = int(round(base_x + dx))
        paste_y = int(round(base_y + dy))
        canvas = Image.new("RGBA", (OUT_W, OUT_H), (0,0,0,0))
        canvas.paste(img, (paste_x, paste_y), img)
        idx = i + 1
        outname = fname_template.format(idx)
        outpath = os.path.join(FRAMES_DIR, outname)
        canvas.save(outpath)

    logger.info("Frame generation complete. Frames saved to: %s", FRAMES_DIR)


def main(argv: Optional[list] = None) -> None:
    """Main entry point.
    
    Args:
        argv: Command-line arguments (optional).
    """
    argv = argv or sys.argv[1:]
    preview_flag = False
    if len(argv) > 0 and argv[0] == "--preview":
        preview_flag = True
    try:
        generate_frames(preview_only=preview_flag)
    except ConfigError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(2)
    except GenerationError as e:
        logger.error("Generation error: %s", e)
        sys.exit(3)
    except Exception as e:
        logger.exception("Unexpected error during frame generation")
        sys.exit(1)

if __name__ == "__main__":
    main()
