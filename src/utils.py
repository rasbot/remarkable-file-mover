"""Utility functions for repo"""

import os
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple, TypedDict

import yaml

from src.constants import (
    IMAGE_CONFIG_PATH,
    TEXT_OVERLAY_IMAGE_DIR,
    IMG_POSITIONS,
    IMG_POSITIONS_HELP,
    TEXT_POSITIONS,
    TEXT_POSITIONS_HELP,
)


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
        "--crop_position",
        "-cp",
        choices=IMG_POSITIONS,
        default="center",
        help=IMG_POSITIONS_HELP,
        metavar="CROP_POSITION",
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
    parser.add_argument(
        "--text_buffer",
        "-tb",
        type=int,
        default=0,
        help="text image buffer value. will be applied to sides and/or top/bottom.",
    )
    parser.add_argument(
        "--text_position",
        "-tp",
        choices=TEXT_POSITIONS,
        default="lower_right",
        help=TEXT_POSITIONS_HELP,
        metavar="TEXT_POSITION",
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


def validate_config_dimensions(
    img_width: int, img_height: int, img_type: str = "target"
) -> None:
    """Validate image dimensions are > 0.

    Args:
        img_width (int): Config image width.
        img_height (int): Config image height.
        img_type (str, optional): Image type. Either "target"
            or "text overlay".
            Defaults to "target".

    Raises:
        ValueError: Raise if image dimensions are <=0.
    """
    if img_width is None or img_width <= 0 or img_height is None or img_height <= 0:
        raise ValueError(
            f"{img_type} dimensions must be positive integers. Got {img_width} width and {img_height} height."
        )


def validate_img_dimensions(
    img_size: Tuple[int, int], target_size: Tuple[int, int]
) -> None:
    """Validate that image dimensions match target dimensions.

    Args:
        img_size (Tuple[int, int]): Tuple of image size (width, height).
        target_size (Tuple[int, int]): Tuple of target image dimensions (width, height).

    Raises:
        ValueError: Raise if image dimensions do not match target dimensions.
    """
    if img_size != target_size:
        raise ValueError(f"Text overlay must be {target_size[0]}x{target_size[1]}")


def load_image_config() -> Dict[str, int]:
    """Load the image config dict and verify dimensions.

    Returns:
        Dict[str, int]: Image config dict.
    """
    image_config = load_config_yaml(yaml_config_path=IMAGE_CONFIG_PATH)
    image_width, image_height = get_image_dimensions_from_config(
        img_config=image_config, img_type="target"
    )
    # validate target image dimensions
    validate_config_dimensions(img_width=image_width, img_height=image_height)
    # validate text overlay image dimensions
    image_width, image_height = get_image_dimensions_from_config(
        img_config=image_config, img_type="text_overlay"
    )
    validate_config_dimensions(img_width=image_width, img_height=image_height)

    return image_config


def get_image_dimensions_from_config(
    img_config: Dict[str, int], img_type: str = "target"
) -> Tuple[int, int]:
    """Get width, height tuple from image config dict.

    Args:
        img_config (Dict[str, int]): Image config dict.
        img_type (str, optional): "target" for target image, else it will
            get dimensions for the text overlay image.

    Returns:
        Tuple[int, int]: width, height tuple.
    """
    if img_type == "target":
        dict_key = "target_img_dims"
    else:
        dict_key = "text_overlay_img_dims"
    width = img_config[dict_key]["width"]
    height = img_config[dict_key]["height"]
    return width, height


class DimensionsDict(TypedDict):
    """DimensionsDict class.

    Args:
        TypedDict (Dict): Width and height of final dimensions.
    """

    width: int
    height: int


class CoordinateDict(TypedDict):
    """CoordinateDict class.

    Args:
        TypedDict (Dict): x and y positions.
    """

    x: int
    y: int


class TextPosition(Enum):
    """Text Position enum.

    Args:
        Enum (str): Text position.
    """

    UPPER_LEFT = "upper_left"
    UPPER_MIDDLE = "upper_middle"
    UPPER_RIGHT = "upper_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_MIDDLE = "middle_middle"
    MIDDLE_RIGHT = "middle_right"
    LOWER_LEFT = "lower_left"
    LOWER_MIDDLE = "lower_middle"
    LOWER_RIGHT = "lower_right"


@dataclass
class ProcessConfig:
    """
    image_path (Path): Full path to image file.
        Defaults to None.
    final_image_dims (DimensionsDict): Final image dimensions dict.
        Defaults to None.
    img_config (Dict[str, int]): Image config values.
        Defaults to None.
    text_image_dims (DimensionsDict): Text overlay image dimensions dict.
        Defaults to None.
    crop_position (Literal["center", "left", "right", "top", "bottom"], optional): Determine
        where to crop the image relative to. Defaults to "center".
    border_width (int, optional): Width of border.
        Defaults to None.
    save_path (Path, optional): Save path for file.
        Defaults to None.
    text_image_path (Path, optional): Path to text overlay file.
        Defaults to None.
    is_inverted (bool, optional): If True, invert the text image colors.
        Defaults to False.
    """

    image_path: Path = None
    final_image_dims: DimensionsDict = None
    img_config: Dict[str, int] = None
    text_image_dims: DimensionsDict = None
    crop_position: Literal["center", "left", "right", "top", "bottom"] = "center"
    border_width: Optional[int] = None
    save_path: Optional[Path] = None
    text_image_path: Optional[Path] = None
    is_inverted: bool = False
    image_buffer: int = 0
    text_position: Literal[
        "upper_left",
        "upper_right",
        "middle_left",
        "middle_right",
        "lower_left",
        "lower_right",
    ] = "lower_right"


@dataclass
class MoveConfig:
    """
    destination_path (Path): Destination file path.
        Defaults to None.
    is_overwritable (bool, optional): If False, raise an exception if
        the file exists. If True, write the file regardless.
        Defaults to False.
    """

    destination_path: Path = None
    is_overwritable: bool = False


def update_processconfig_from_args(
    config: ProcessConfig, args: Namespace
) -> ProcessConfig:
    """Update ProcessConfig instance with variables from
    command line args Namespace.

    Args:
        config (ProcessConfig): Instance of ProcessConfig.
        args (Namespace): Argparse namespace.

    Returns:
        ProcessConfig: Updated ProcessConfig instance.
    """
    config.image_path = Path(args.source)
    config.crop_position = args.crop_position
    config.border_width = args.border
    config.text_image_path = get_text_overlay_path(text_overlay_filename=args.textfile)
    config.is_inverted = args.invert
    config.image_buffer = args.text_buffer
    config.text_position = TextPosition(args.text_position)
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
    if text_overlay_filename is None:
        return None
    text_overlay_filepath = None
    if text_overlay_filename:
        text_overlay_filepath = os.path.join(
            TEXT_OVERLAY_IMAGE_DIR, text_overlay_filename
        )
    if not os.path.exists(text_overlay_filepath):
        err_msg = (
            f"{text_overlay_filepath} does not exist. "
            + "Please add it or choose a different file."
        )
        raise FileNotFoundError(err_msg)
    return Path(text_overlay_filepath)
