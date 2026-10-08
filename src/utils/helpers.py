"""Helper utilities for configuration loading and structured logging."""

import logging
import os
from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv

# Load environment variables on module import
load_dotenv()


def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """Load application configuration from a YAML file.

    Args:
        config_path: Relative or absolute path to the YAML config file.

    Returns:
        Dictionary containing configuration parameters.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_logger(name: str, log_file: str = "logs/app.log") -> logging.Logger:
    """Create and configure a standard application logger.

    Args:
        name: Name of the logger, typically __name__.
        log_file: Path to the destination log file.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
