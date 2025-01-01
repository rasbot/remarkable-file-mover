"""Move a file to a destination and rename it to 'suspended.png'"""

import argparse
import os
import shutil
from pathlib import Path

from src.constants import CONFIG_PATH
from src.utils import ProtectedFile, ConfigKey, get_config_path


def get_destination_path(config_path: Path) -> Path:
    """Read in the value of the desitination path from
    the config file (value for `SOURCE_PATH` in config).

    Args:
        config_path (Path): Path to config file.

    Returns:
        Path: Path to move image to.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"{config_path} file was not found! Please create it (see README)."
        )
    with open(config_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    destination_path = None
    for line in lines:
        if line.startswith("SOURCE_PATH="):
            destination_path = line.split("=", 1)[1].strip()

    return Path(destination_path)


def move_file(
    source_path: Path, destination_path: Path, is_overwritable: bool = False
) -> None:
    """Move a source file (full file path) to a destination
    (full file path).

    Args:
        source_path (Path): Source file path.
        destination_path (Path): Destination file path.
        is_overwritable (bool, optional): If False, raise an exception if
            the file exists. If True, write the file regardless.
            Defaults to False.

    Raises:
        ProtectedFile: Raise if a file exists and `is_overwritable` = False
            to prevent it from being overwritten.
    """
    if not is_overwritable and os.path.exists(destination_path):
        raise ProtectedFile(file_path=destination_path)
    try:
        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Copy the file, overwriting if it exists
        shutil.copy2(source_path, destination_path)
        print(f"Successfully moved {source_path} to {destination_path}")

    except Exception as e:
        print(f"Error moving file: {str(e)}")


def main():
    """Main function to move and rename a file"""
    parser = argparse.ArgumentParser(
        description="Move and rename a file to a specific location."
    )
    parser.add_argument(
        "--source", "-s", type=str, required=True, help="Source file path"
    )
    parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        help="If passed, overwrite image if it exists.",
    )

    args = parser.parse_args()

    source_path = args.source
    is_overwritable = args.overwrite
    destination_path = get_config_path(
        config_path=CONFIG_PATH, config_key=ConfigKey.DESTINATION_DIR
    )
    move_file(
        source_path=source_path,
        destination_path=destination_path,
        is_overwritable=is_overwritable,
    )


if __name__ == "__main__":
    main()
