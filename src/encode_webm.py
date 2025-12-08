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
    print("Running ffmpeg:")
    print(" ".join(cmd))
    # run inside FRAMES_DIR
    proc = subprocess.run(cmd, cwd=FRAMES_DIR)
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg failed with exit code: " + str(proc.returncode))
    print("Encoding finished. Output:", outpath)

if __name__ == "__main__":
    if not os.path.isdir(FRAMES_DIR):
        raise FileNotFoundError("Frames directory not found: " + FRAMES_DIR)
    pattern, outpath = build_pattern_and_out()
    if ffmpeg_exists():
        run_ffmpeg(pattern, outpath)
    else:
        print("ffmpeg not found on PATH. Copy/paste the following command on a machine with ffmpeg:")
        print()
        print("cd", FRAMES_DIR)
        print(f"{FFMPEG_BIN} -framerate {FPS} -i {pattern} -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 {outpath}")
        print()
