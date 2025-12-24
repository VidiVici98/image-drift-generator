import logging
import os
from typing import Optional


def setup_logger(name: str = __name__, level_env: str = "LOG_LEVEL") -> logging.Logger:
    """Create and return a configured logger.

    Args:
        name: Logger name.
        level_env: Environment variable name for log level (defaults to LOG_LEVEL).
        
    Returns:
        Configured Logger instance.

    - Reads `LOG_LEVEL` from environment (defaults to INFO).
    - Outputs to stdout with a compact formatter including level and name.
    """
    level_name = os.environ.get(level_env, "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # If handlers already attached, avoid duplicate handlers
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    return logger
