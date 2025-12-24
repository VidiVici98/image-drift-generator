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
from src.errors import ConfigError, GenerationError, EncoderError


def make_sample_image(path: str, size: tuple = (40, 24), color: tuple = (255, 0, 0, 255)) -> None:
    """Create a sample test image."""
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
    with pytest.raises(EncoderError):
        ew.run_ffmpeg("pattern.png", str(tmp_path / "out.webm"))


# Additional comprehensive tests
class TestConfigValidation:
    """Test config validation."""

    def test_validate_config_empty_input_image(self, monkeypatch):
        """Test validation fails with empty INPUT_IMAGE."""
        monkeypatch.setattr(gf, "INPUT_IMAGE", "")
        with pytest.raises(ConfigError, match="INPUT_IMAGE"):
            gf.validate_config()

    def test_validate_config_negative_dimensions(self, monkeypatch):
        """Test validation fails with negative canvas dimensions."""
        monkeypatch.setattr(gf, "INPUT_IMAGE", "valid.png")
        monkeypatch.setattr(gf, "OUT_W", -100)
        with pytest.raises(ConfigError, match="OUT_W"):
            gf.validate_config()

    def test_validate_config_zero_fps(self, monkeypatch):
        """Test validation fails with zero FPS."""
        monkeypatch.setattr(gf, "INPUT_IMAGE", "valid.png")
        monkeypatch.setattr(gf, "OUT_W", 1080)
        monkeypatch.setattr(gf, "OUT_H", 1920)
        monkeypatch.setattr(gf, "DURATION_SECONDS", 30.0)
        monkeypatch.setattr(gf, "FPS", 0)
        with pytest.raises(ConfigError, match="FPS"):
            gf.validate_config()

    def test_validate_config_invalid_motion_mode(self, monkeypatch):
        """Test validation fails with invalid motion mode."""
        monkeypatch.setattr(gf, "INPUT_IMAGE", "valid.png")
        monkeypatch.setattr(gf, "OUT_W", 1080)
        monkeypatch.setattr(gf, "OUT_H", 1920)
        monkeypatch.setattr(gf, "DURATION_SECONDS", 30.0)
        monkeypatch.setattr(gf, "FPS", 30)
        monkeypatch.setattr(gf, "TOTAL_FRAMES", 900)
        monkeypatch.setattr(gf, "SCALE", 0.5)
        monkeypatch.setattr(gf, "MOTION_MODE", "invalid")
        with pytest.raises(ConfigError, match="MOTION_MODE"):
            gf.validate_config()

    def test_validate_config_invalid_base_pos_mode(self, monkeypatch):
        """Test validation fails with invalid base position mode."""
        monkeypatch.setattr(gf, "INPUT_IMAGE", "valid.png")
        monkeypatch.setattr(gf, "OUT_W", 1080)
        monkeypatch.setattr(gf, "OUT_H", 1920)
        monkeypatch.setattr(gf, "DURATION_SECONDS", 30.0)
        monkeypatch.setattr(gf, "FPS", 30)
        monkeypatch.setattr(gf, "TOTAL_FRAMES", 900)
        monkeypatch.setattr(gf, "SCALE", 0.5)
        monkeypatch.setattr(gf, "MOTION_MODE", "sine")
        monkeypatch.setattr(gf, "BASE_POS_MODE", "invalid")
        with pytest.raises(ConfigError, match="BASE_POS_MODE"):
            gf.validate_config()

    def test_validate_config_passes_with_valid_config(self, monkeypatch, tmp_path):
        """Test validation passes with valid configuration."""
        inp = tmp_path / "in.png"
        make_sample_image(str(inp))
        
        monkeypatch.setattr(gf, "INPUT_IMAGE", str(inp))
        monkeypatch.setattr(gf, "OUT_W", 1080)
        monkeypatch.setattr(gf, "OUT_H", 1920)
        monkeypatch.setattr(gf, "DURATION_SECONDS", 30.0)
        monkeypatch.setattr(gf, "FPS", 30)
        monkeypatch.setattr(gf, "TOTAL_FRAMES", 900)
        monkeypatch.setattr(gf, "SCALE", 0.5)
        monkeypatch.setattr(gf, "MOTION_MODE", "perlin")
        monkeypatch.setattr(gf, "BASE_POS_MODE", "center")
        
        # Should not raise
        gf.validate_config()


class TestMotionCalculations:
    """Test motion offset calculations."""

    def test_perlin_like_offsets_returns_tuple(self, monkeypatch):
        """Test that perlin offsets return a float tuple."""
        from opensimplex import OpenSimplex
        gen = OpenSimplex(42)
        dx, dy = gf.perlin_like_offsets(gen, 1.0, 10.0, 5.0, 8.0)
        assert isinstance(dx, float)
        assert isinstance(dy, float)

    def test_sine_offsets_returns_tuple(self):
        """Test that sine offsets return a float tuple."""
        dx, dy = gf.sine_offsets(0.5, 10.0, 50.0, 75.0, 1.0, 1.0)
        assert isinstance(dx, float)
        assert isinstance(dy, float)

    def test_sine_offsets_at_zero_time(self):
        """Test sine offset at t=0."""
        dx, dy = gf.sine_offsets(0.0, 10.0, 100.0, 100.0, 1.0, 1.0)
        assert abs(dx) < 0.01  # Should be close to 0


class TestEncoderFunctions:
    """Test encoder utility functions."""

    def test_zero_pad_width_single_digit(self):
        """Test padding width for single digit frame count."""
        pad = ew.zero_pad_width(5)
        assert pad == 4

    def test_zero_pad_width_large_number(self):
        """Test padding width for large frame count."""
        pad = ew.zero_pad_width(10000)
        assert pad == 5

    def test_build_pattern_and_out(self, monkeypatch, tmp_path):
        """Test pattern and output path building."""
        monkeypatch.setattr(ew, "TOTAL_FRAMES", 900)
        monkeypatch.setattr(ew, "BASENAME", "test")
        monkeypatch.setattr(ew, "FINAL_DIR", str(tmp_path))
        
        pattern, outpath = ew.build_pattern_and_out()
        assert pattern == "test_%04d.png"
        assert outpath.endswith(".webm")
        assert "test.webm" in outpath

    def test_ffmpeg_exists_returns_bool(self):
        """Test that ffmpeg_exists returns a boolean."""
        result = ew.ffmpeg_exists()
        assert isinstance(result, bool)


class TestPreviewGeneration:
    """Test preview image generation."""

    def test_build_preview_creates_file(self, tmp_path):
        """Test that preview building creates a file."""
        from PIL import Image
        inp_img = Image.new("RGBA", (40, 24), (255, 0, 0, 255))
        out_path = tmp_path / "preview.png"
        
        gf.build_preview(200, 100, inp_img, (50, 25), str(out_path))
        
        assert out_path.exists()
        result_img = Image.open(out_path)
        assert result_img.size == (200, 100)
        assert result_img.mode == "RGBA"
