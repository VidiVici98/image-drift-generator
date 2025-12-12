import os
import sys
import math

# make sure repo root is on path so tests can import src scripts
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.generate_frames import sine_offsets, perlin_like_offsets, make_noise


def test_sine_offsets_basic():
    dx, dy = sine_offsets(t_seconds=0.25, duration=1.0, amp_x=10, amp_y=5, cycles_x=1, cycles_y=2)
    # expect values in range [-amp, amp]
    assert -10.0 <= dx <= 10.0
    assert -5.0 <= dy <= 5.0
    # sanity: at t=0 amplitude should be ~0 for sine with cycles integer
    dx0, dy0 = sine_offsets(t_seconds=0.0, duration=1.0, amp_x=10, amp_y=5, cycles_x=1, cycles_y=1)
    assert abs(dx0) < 1e-6


def test_perlin_like_offsets_bounds():
    gen, seed = make_noise(seed="42")
    dx, dy = perlin_like_offsets(gen, t_seconds=0.5, amp_x=20, amp_y=15, timescale_seconds=2.0)
    assert -20.0 <= dx <= 20.0
    assert -15.0 <= dy <= 15.0


def test_make_noise_deterministic():
    g1, s1 = make_noise(seed="123")
    g2, s2 = make_noise(seed="123")
    assert s1 == s2
