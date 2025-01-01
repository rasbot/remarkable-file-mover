"""Process and move / rename image file."""

import argparse
import os
from pathlib import Path
from typing import Dict, Literal

import src.constants as c
import src.utils as u
from src.process_image import get_processed_output_path, process_image, DimensionsDict
from src.utils import get_config_path, ProtectedFile, ConfigKey
from src.move_file import move_file


def process_and_move(
    source_path: Path,
    img_dims_dict: DimensionsDict,
    img_config_dict: Dict[str, int],
    position: Literal["center", "left", "right", "top", "bottom"] = "center",
    border: int = None,
    text_image_path: Path = None,
    is_inverted: bool = False,
    is_overwritable: bool = False,
) -> None:
    # TODO: update docstring
    """Process an image and move / rename it.

    Args:
        source_path (Path): Initial source image path.
        img_dims_dict (DimensionsDict): Dict of final image dimensions.
        position (Literal["center", "left", "right", "top", "bottom"], optional): Determine
            where to crop the image relative to. Defaults to "center".
        border (int): Border thickness if needed.
            Defaults to None.
        is_overwritable (bool, optional): If False, raise an exception if
            the file exists. If True, write the file regardless.
            Defaults to False.

    Raises:
        ProtectedFile: Raise if a file exists and `is_overwritable` = False
            to prevent it from being overwritten.
    """
    processed_path = get_processed_output_path(input_path=source_path)
    # make sure we can overwrite the file if it exists before processing
    if not is_overwritable and os.path.exists(processed_path):
        raise ProtectedFile(file_path=processed_path)

    process_image(
        image_path=source_path,
        final_image_dims=img_dims_dict,
        img_config=img_config_dict,
        crop_position=position,
        border_width=border,
        text_image_path=text_image_path,
        is_inverted=is_inverted,
    )
    destination_path = get_config_path(
        config_path=c.CONFIG_PATH, config_key=ConfigKey.SOURCE_PATH
    )
    move_file(
        source_path=processed_path,
        destination_path=destination_path,
        is_overwritable=is_overwritable,
    )


def main():
    """Main function to process and save image."""
    parser = argparse.ArgumentParser(
        description="Crop and resize an image to specific dimensions."
    )
    u.add_process_image_args(parser)
    u.add_move_file_args(parser, require_source=False)  # Don't add source again

    args = parser.parse_args()
    input_file_path = args.source
    position = args.position
    border = args.border
    text_overlay_filename = args.textfile
    is_inverted = args.invert
    overwrite = args.overwrite

    text_overlay_filepath = u.get_text_overlay_path(
        text_overlay_filename=text_overlay_filename
    )
    img_config_dict = u.load_config_yaml(c.IMAGE_CONFIG_PATH)
    width = img_config_dict["target_img_dims"]["width"]
    height = img_config_dict["target_img_dims"]["height"]
    final_image_dims_dict = DimensionsDict(width=width, height=height)

    process_and_move(
        source_path=input_file_path,
        img_dims_dict=final_image_dims_dict,
        img_config_dict=img_config_dict,
        position=position,
        border=border,
        text_image_path=text_overlay_filepath,
        is_inverted=is_inverted,
        is_overwritable=overwrite,
    )


if __name__ == "__main__":
    main()
