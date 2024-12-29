"""Move a file to a destination and rename it to 'suspended.png'"""

import argparse
import os
import shutil
from pathlib import Path

from src.constants import CONFIG_PATH


class ProtectedFile(Exception):
    """Error class to handle protected file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.message = (
            f"File path {file_path} exists and is protected from being overwritten. "
            "Move the existing file or pass `is_overwritable` = True in move_file."
        )

        super().__init__(self.message)


def get_destination_path(config_path: Path) -> Path:
    """Read in the value of the desitination path from
    the config file (value for `SOURCE_PATH` in config).

    Args:
        config_path (Path): Path to config file.

    Returns:
        Path: Path to move image to.
    """
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

    args = parser.parse_args()

    source_path = args.source
    destination_path = get_destination_path(config_path=CONFIG_PATH)
    move_file(source_path=source_path, destination_path=destination_path)


if __name__ == "__main__":
    main()
