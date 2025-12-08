# config.sh -- edit these values

# INPUT IMAGE (must support alpha if you want transparent output)
INPUT_IMAGE="input/logo-skull-test-1.webp"

# OUTPUT layout
OUTPUT_DIR="output"             # base output directory
BASENAME="testframe"            # base name for frames and final file
FRAMES_DIR="${OUTPUT_DIR}/frames"
FINAL_DIR="${OUTPUT_DIR}/final"

# CANVAS (portrait default)
OUT_W=1080
OUT_H=1920

# TIMING
DURATION_SECONDS=10
FPS=30
TOTAL_FRAMES=$((DURATION_SECONDS * FPS))

# IMAGE SCALING: prefer TARGET_PIXEL_WIDTH; if empty, SCALE multiplier will be used.
TARGET_PIXEL_WIDTH=600   # set desired width in px, or leave empty
SCALE=1               # fallback multiplier if TARGET_PIXEL_WIDTH is empty

# BASE POSITION (top-left of scaled image on canvas), in pixels.
# If you want centered, set BASE_POS_MODE="center" and use BASE_CENTER_OFFSET below.
# Otherwise set BASE_POS_MODE="coords" and specify BASE_X and BASE_Y.
BASE_POS_MODE="coords"         # "center" or "coords"
BASE_CENTER_OFFSET_X=0
BASE_CENTER_OFFSET_Y=0
BASE_X=100
BASE_Y=500

# MOTION MODE: "perlin" or "sine"
MOTION_MODE="perlin"

# MOTION PARAMETERS (absolute pixels)
AMP_X=75       # horizontal amplitude (px)
AMP_Y=50       # vertical amplitude (px)

# NOISE timescale in seconds (larger = slower drift)
NOISE_TIMESCALE_SECONDS=8

# NOISE seed: empty => random per run; set integer for reproducible runs
NOISE_SEED=""

# SINE params (if MOTION_MODE == "sine")
SINE_CYCLES_X=0.6
SINE_CYCLES_Y=0.5

# Naming & padding
FRAME_PREFIX="${BASENAME}"
# padding will be auto-calculated from TOTAL_FRAMES

# FFmpeg binary (if not on PATH, set full path here)
FFMPEG_BIN="ffmpeg"

# End of config
