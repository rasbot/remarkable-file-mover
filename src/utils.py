import os
from enum import Enum
from pathlib import Path
from typing import Any


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