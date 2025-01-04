"""Process and move / rename image file."""

import argparse
import os

from src.constants import CONFIG_PATH
from src.move_file import move_file
from src.process_image import DimensionsDict, get_processed_output_path, process_image
from src.utils import (
    ConfigKey,
    MoveConfig,
    ProcessConfig,
    ProtectedFile,
    add_move_file_args,
    add_process_image_args,
    get_config_path,
    get_image_dimensions_from_config,
    load_image_config,
    update_processconfig_from_args,
)


def process_and_move(
    process_config: ProcessConfig,
    move_config: MoveConfig,
) -> None:
    """Process an image and move / rename it.

    Args:
        process_config (ProcessConfig): ProcessConfig instance.
        move_config (MoveConfig): MoveConfig instance.

    Raises:
        ProtectedFile: Raise if a file exists and `is_overwritable` = False
            to prevent it from being overwritten.
    """
    processed_path = get_processed_output_path(input_path=process_config.image_path)
    # make sure we can overwrite the file if it exists before processing
    is_overwritable = move_config.is_overwritable
    if not is_overwritable and os.path.exists(processed_path):
        raise ProtectedFile(file_path=processed_path)

    process_image(process_config=process_config)
    destination_path = get_config_path(
        config_path=CONFIG_PATH, config_key=ConfigKey.SOURCE_PATH
    )
    move_config.destination_path = destination_path
    move_file(source_path=processed_path, move_config=move_config)


def main():
    """Main function to process and save image."""
    parser = argparse.ArgumentParser(
        description="Crop and resize an image to specific dimensions."
    )
    add_process_image_args(parser)
    add_move_file_args(parser, require_source=False)  # Don't add source again

    args = parser.parse_args()
    img_config = load_image_config()
    width, height = get_image_dimensions_from_config(img_config=img_config)

    process_config = ProcessConfig()
    final_image_dims_dict = DimensionsDict(width=width, height=height)
    process_config.final_image_dims = final_image_dims_dict
    process_config.img_config = img_config
    process_config = update_processconfig_from_args(config=process_config, args=args)

    move_config = MoveConfig()
    destination_path = get_config_path(
        config_path=CONFIG_PATH, config_key=ConfigKey.DESTINATION_DIR
    )
    move_config.destination_path = destination_path
    move_config.is_overwritable = args.overwrite
    process_and_move(process_config=process_config, move_config=move_config)


if __name__ == "__main__":
    main()
