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
from PIL import Image, ImageDraw
import numpy as np
from opensimplex import OpenSimplex

from .logging_config import setup_logger
from .errors import ConfigError, GenerationError

logger = setup_logger(__name__)

# Helper: read env variables with defaults
def env(name, default=None):
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

# Utility
def verbose_print(*a, **k):
    # keep backward-compatible wrapper; route to logger.info
    logger.info("%s", " ".join(str(x) for x in a))

def ensure_dirs():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    os.makedirs(FINAL_DIR, exist_ok=True)

def load_and_scale_image():
    if not os.path.isfile(INPUT_IMAGE):
        raise ConfigError("Input image not found: " + INPUT_IMAGE)
    img = Image.open(INPUT_IMAGE).convert("RGBA")
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

def compute_base_position(img_w, img_h):
    if BASE_POS_MODE == "center":
        x = (OUT_W - img_w) // 2 + BASE_CENTER_OFFSET_X
        y = (OUT_H - img_h) // 2 + BASE_CENTER_OFFSET_Y
        return x, y
    else:
        return BASE_X, BASE_Y

def zero_pad_width(total):
    return max(4, len(str(int(total))))

def build_preview(canvas_w, canvas_h, img, paste_xy, outpath):
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
def make_noise(seed=None):
    if seed is None or seed == "":
        seed_int = random.randint(0, 2**30-1)
    else:
        try:
            seed_int = int(seed)
        except:
            seed_int = random.randint(0, 2**30-1)
    gen = OpenSimplex(seed_int)
    return gen, seed_int

def perlin_like_offsets(gen, t_seconds, amp_x, amp_y, timescale_seconds, seed_offset_x=0.0, seed_offset_y=0.0):
    # produce offsets using opensimplex noise in an open domain
    # timescale_seconds maps to frequency (freq = 1/timescale)
    freq = 1.0 / max(1e-6, timescale_seconds)
    nx = gen.noise2d(t_seconds * freq + seed_offset_x, 0.0)
    ny = gen.noise2d(t_seconds * freq + seed_offset_y, 33.33)
    # noise output ~[-1,1]
    dx = nx * amp_x
    dy = ny * amp_y
    return dx, dy

def sine_offsets(t_seconds, duration, amp_x, amp_y, cycles_x, cycles_y):
    t_norm = t_seconds / max(1e-9, duration)
    dx = math.sin(2 * math.pi * (t_norm * cycles_x)) * amp_x
    dy = math.sin(2 * math.pi * (t_norm * cycles_y) + 1.7) * amp_y
    return dx, dy

def generate_frames(preview_only=False):
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

    logger.info("Generating frames: %d", TOTAL_FRAMES)
    for i in range(TOTAL_FRAMES):
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
        if idx % 100 == 0 or idx == TOTAL_FRAMES:
            logger.info("wrote %d/%d", idx, TOTAL_FRAMES)

    logger.info("Frame generation complete. Frames saved to: %s", FRAMES_DIR)


def main(argv=None):
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
