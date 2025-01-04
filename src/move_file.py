"""Move a file to a destination and rename it to 'suspended.png'"""

import argparse
import os
import shutil
from pathlib import Path

from src.constants import CONFIG_PATH
from src.utils import (
    ConfigKey,
    ProtectedFile,
    MoveConfig,
    add_move_file_args,
    get_config_path,
)


def move_file(source_path: Path, move_config: MoveConfig) -> None:
    """Move a source file (full file path) to a destination
    (full file path).

    Args:
        source_path (Path): Source file path.
        move_config (MoveConfig): MoveConfig instance.

    Raises:
        ProtectedFile: Raise if a file exists and `is_overwritable` = False
            to prevent it from being overwritten.
    """
    # unpack dataclass
    destination_path = move_config.destination_path
    is_overwritable = move_config.is_overwritable

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
    move_config = MoveConfig()
    destination_path = get_config_path(
        config_path=CONFIG_PATH, config_key=ConfigKey.DESTINATION_DIR
    )
    move_config.destination_path = destination_path
    move_config.is_overwritable = args.overwrite
    move_file(source_path=source_path, move_config=move_config)


if __name__ == "__main__":
    main()
