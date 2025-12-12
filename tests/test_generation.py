import os
import sys
import shutil

import pytest

# ensure repo root on path so tests can import src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import generate_frames as gf
from src import encode_webm as ew
from src.errors import ConfigError


def make_sample_image(path, size=(40, 24), color=(255, 0, 0, 255)):
    from PIL import Image

    img = Image.new("RGBA", size, color)
    img.save(path)


def test_load_and_scale_image_target_width(tmp_path, monkeypatch):
    inp = tmp_path / "in.png"
    make_sample_image(str(inp), size=(80, 40))

    # monkeypatch module globals to point at the sample image
    monkeypatch.setattr(gf, "INPUT_IMAGE", str(inp))
    monkeypatch.setattr(gf, "TARGET_PIXEL_WIDTH", "40")
    img = gf.load_and_scale_image()
    assert img.size[0] == 40


def test_compute_base_position_modes(monkeypatch):
    # center mode
    monkeypatch.setattr(gf, "OUT_W", 200)
    monkeypatch.setattr(gf, "OUT_H", 100)
    monkeypatch.setattr(gf, "BASE_POS_MODE", "center")
    monkeypatch.setattr(gf, "BASE_CENTER_OFFSET_X", 5)
    monkeypatch.setattr(gf, "BASE_CENTER_OFFSET_Y", -3)
    x, y = gf.compute_base_position(50, 20)
    assert x == (200 - 50) // 2 + 5
    assert y == (100 - 20) // 2 - 3

    # coords mode
    monkeypatch.setattr(gf, "BASE_POS_MODE", "coords")
    monkeypatch.setattr(gf, "BASE_X", 7)
    monkeypatch.setattr(gf, "BASE_Y", 9)
    x2, y2 = gf.compute_base_position(10, 10)
    assert (x2, y2) == (7, 9)


def test_generate_preview_writes_file(tmp_path, monkeypatch):
    # prepare an input image and small dirs
    inp = tmp_path / "in.png"
    make_sample_image(str(inp), size=(32, 16))

    out_dir = tmp_path / "out"
    frames_dir = out_dir / "frames"
    final_dir = out_dir / "final"

    monkeypatch.setattr(gf, "INPUT_IMAGE", str(inp))
    monkeypatch.setattr(gf, "OUTPUT_DIR", str(out_dir))
    monkeypatch.setattr(gf, "FRAMES_DIR", str(frames_dir))
    monkeypatch.setattr(gf, "FINAL_DIR", str(final_dir))
    monkeypatch.setattr(gf, "BASENAME", "unittest")
    monkeypatch.setattr(gf, "OUT_W", 128)
    monkeypatch.setattr(gf, "OUT_H", 64)

    # run preview-only generation
    gf.generate_frames(preview_only=True)

    preview_path = out_dir / "unittest_preview.png"
    assert preview_path.exists()


def test_load_and_scale_raises_on_missing_input(monkeypatch):
    monkeypatch.setattr(gf, "INPUT_IMAGE", "/no/such/file.png")
    with pytest.raises(ConfigError):
        gf.load_and_scale_image()


def test_encode_run_ffmpeg_raises_encodererror_for_missing_dir(tmp_path, monkeypatch):
    # point FRAMES_DIR at a non-existent directory and call run_ffmpeg
    nonexist = tmp_path / "nope"
    monkeypatch.setattr(ew, "FRAMES_DIR", str(nonexist))
    # pattern/out are irrelevant since cwd doesn't exist; should raise EncoderError
    with pytest.raises(ew.EncoderError):
        ew.run_ffmpeg("pattern.png", str(tmp_path / "out.webm"))
