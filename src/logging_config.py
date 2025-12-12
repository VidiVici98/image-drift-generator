import logging
import os


def setup_logger(name=__name__, level_env="LOG_LEVEL"):
    """Create and return a configured logger.

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
