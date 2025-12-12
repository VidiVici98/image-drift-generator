#!/usr/bin/env python3
"""
encode_webm.py

Reads environment config exported by run.sh and attempts to encode the PNG sequence
in FRAMES_DIR into a VP9 WebM with alpha in FINAL_DIR.
If ffmpeg not found, prints the exact ffmpeg command to run elsewhere.
"""

import os
import shutil
import subprocess
import sys

from .logging_config import setup_logger
from .errors import EncoderError

logger = setup_logger(__name__)

def env(name, default=None):
    v = os.environ.get(name, None)
    if v is None:
        return default
    return v

FRAMES_DIR = env("FRAMES_DIR", "output/frames")
FINAL_DIR = env("FINAL_DIR", "output/final")
BASENAME = env("BASENAME", "testframe")
FPS = int(env("FPS", 30))
TOTAL_FRAMES = int(env("TOTAL_FRAMES", 30*30))
FFMPEG_BIN = env("FFMPEG_BIN", "ffmpeg")

def zero_pad_width(total):
    return max(4, len(str(int(total))))

def build_pattern_and_out():
    pad = zero_pad_width(TOTAL_FRAMES)
    pattern = f"{BASENAME}_%0{pad}d.png"
    outpath = os.path.join(FINAL_DIR, f"{BASENAME}.webm")
    return pattern, outpath

def ffmpeg_exists():
    return shutil.which(FFMPEG_BIN) is not None

def run_ffmpeg(pattern, outpath):
    cmd = [
        FFMPEG_BIN, "-y",
        "-framerate", str(FPS),
        "-i", pattern,
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        "-auto-alt-ref", "0",
        outpath
    ]
    logger.info("Running ffmpeg: %s", " ".join(cmd))
    # run inside FRAMES_DIR
    try:
        proc = subprocess.run(cmd, cwd=FRAMES_DIR)
    except Exception as e:
        logger.exception("Failed to start ffmpeg process")
        raise EncoderError("ffmpeg start failed") from e
    if proc.returncode != 0:
        logger.error("ffmpeg failed with exit code: %s", proc.returncode)
        raise EncoderError(f"ffmpeg failed with exit code: {proc.returncode}")
    logger.info("Encoding finished. Output: %s", outpath)

def main(argv=None):
    try:
        if not os.path.isdir(FRAMES_DIR):
            logger.error("Frames directory not found: %s", FRAMES_DIR)
            raise EncoderError("frames directory missing")
        pattern, outpath = build_pattern_and_out()
        if ffmpeg_exists():
            run_ffmpeg(pattern, outpath)
        else:
            logger.warning("ffmpeg not found on PATH. Printing command to run elsewhere.")
            print()
            print("cd", FRAMES_DIR)
            print(f"{FFMPEG_BIN} -framerate {FPS} -i {pattern} -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 {outpath}")
            print()
        return 0
    except EncoderError as e:
        logger.error("Encoding failed: %s", e)
        return 2
    except Exception:
        logger.exception("Unexpected error in encoder")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
