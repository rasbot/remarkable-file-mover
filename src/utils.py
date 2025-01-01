"""Utility functions for repo"""

from argparse import ArgumentParser
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

import src.constants as c


def add_process_image_args(parser: ArgumentParser) -> None:
    """Add arguments used by process_image.py to an existing parser."""
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        help="Path to unprocessed image source file",
        required=True,
    )
    parser.add_argument(
        "--position",
        "-p",
        choices=["center", "left", "right", "top", "bottom"],
        default="center",
        help="Position to crop from (default: center)",
    )
    parser.add_argument(
        "--border",
        "-b",
        nargs="?",
        type=int,
        const=30,
        help="Add white border with specified width (default: 30 if flag is used)",
    )
    parser.add_argument(
        "--textfile",
        "-t",
        nargs="?",
        type=str,
        const="text_overlay.png",
        help="File name of text overlay file, if used.",
    )
    parser.add_argument(
        "--invert",
        "-i",
        action="store_true",
        help="Invert the text color (black to white or white to black)",
    )


def add_move_file_args(parser: ArgumentParser, require_source: bool = True) -> None:
    """Add arguments used by move_file.py to an existing parser."""
    if require_source:
        parser.add_argument(
            "--source",
            "-s",
            type=str,
            help="Path to unprocessed image source file",
            required=True,
        )
    parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        help="Overwrite existing file if it exists",
    )


def load_config_yaml(yaml_config_path: Path) -> Dict[str, int]:
    """Load a yaml file into a dict.

    Args:
        yaml_config_path (Path): yaml path.

    Returns:
        Dict[str, int]: Config dict.
    """
    with open(yaml_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


class ProtectedFile(Exception):
    """Error class to handle protected file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.message = (
            f"File path {file_path} exists and is protected from being overwritten. "
            "Move the existing file or pass `is_overwritable` = True in move_file."
        )

        super().__init__(self.message)


class ConfigKey(Enum):
    """Config key enum.

    Args:
        Enum (str): Config key.
    """

    SOURCE_PATH = "SOURCE_PATH"
    TEXT_IMAGE_PATH = "TEXT_IMAGE_PATH"
    DESTINATION_DIR = "DESTINATION_DIR"


def get_config_path(config_path: Path, config_key: ConfigKey) -> Any:
    """Read in the path value of a config key from
    the config file.

    Args:
        config_path (Path): Path to config file.
        config_key (ConfigKey): Config key enum.

    Raises:
        FileNotFoundError: Raised if the config file does not
            exist.
        KeyError: Raised if the config key is not found in the
            file.

    Returns:
        Path: Path of config key / value.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"{config_path} file was not found! Please create it (see README)."
        )
    with open(config_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    config_path = None
    no_key = True
    for line in lines:
        if line.startswith(f"{config_key.value}="):
            no_key = False
            config_path = line.split("=", 1)[1].strip()
    if no_key:
        raise KeyError(f"Config key ({config_key.value}) not found.")

    return Path(config_path)


def get_text_overlay_path(text_overlay_filename: str):
    """Get the path for the text overlay file.

    Args:
        text_overlay_filename (str): Text overlay filename.

    Raises:
        FileNotFoundError: Raised if the file does not exist.

    Returns:
        Path: Path of text overlay file.
    """
    text_overlay_filepath = None
    if text_overlay_filename:
        text_overlay_filepath = os.path.join(
            c.TEXT_OVERLAY_IMAGE_DIR, text_overlay_filename
        )
    if not os.path.exists(text_overlay_filepath):
        err_msg = (
            f"{text_overlay_filepath} does not exist. "
            + "Please add it or choose a different file."
        )
        raise FileNotFoundError(err_msg)
    return Path(text_overlay_filepath)
