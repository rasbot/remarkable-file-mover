"""Move a file to a destination and rename it to 'suspended.png'"""

import argparse
import os
import shutil
from pathlib import Path

from src.constants import CONFIG_PATH
from src.utils import (ConfigKey, ProtectedFile, add_move_file_args,
                       get_config_path)


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
    add_move_file_args(parser=parser)

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
