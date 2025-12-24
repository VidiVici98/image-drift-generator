"""Custom exceptions for image-drift-generator."""


class ImageDriftError(Exception):
    """Base exception for image-drift-generator."""


class ConfigError(ImageDriftError):
    """Raised when configuration is invalid or missing."""


class GenerationError(ImageDriftError):
    """Raised when frame generation fails."""


class EncoderError(ImageDriftError):
    """Raised when encoding fails (ffmpeg issues, etc.)."""
