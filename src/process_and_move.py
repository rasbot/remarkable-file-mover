"""Process and move / rename image file."""

import argparse
import os
from pathlib import Path
from typing import Literal

from src.constants import CONFIG_PATH
from src.process_image import get_processed_output_path, process_image, DimensionsDict
from src.move_file import ProtectedFile, get_destination_path, move_file


def process_and_move(
    source_path: Path,
    dimensions_dict: DimensionsDict,
    position: Literal["center", "left", "right", "top", "bottom"] = "center",
    border: int = None,
    is_overwritable: bool = False,
) -> None:
    """Process an image and move / rename it.

    Args:
        source_path (Path): Initial source image path.
        dimensions_dict (DimensionsDict): Dict of final image dimensions.
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
        final_image_dims=dimensions_dict,
        crop_position=position,
        border_width=border,
        save_path=processed_path,
    )
    destination_path = get_destination_path(config_path=CONFIG_PATH)
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
    parser.add_argument(
        "--source", "-s", type=str, help="Path to input image", required=True
    )
    parser.add_argument(
        "--width", "-w", type=int, default=1620, help="Target width (default: 1620)"
    )
    parser.add_argument(
        "--height", "-ht", type=int, default=2160, help="Target height (default: 2160)"
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
        "--overwrite",
        "-o",
        action="store_true",
        help="If passed, overwrite image if it exists.",
    )

    args = parser.parse_args()
    input_file_path = args.source
    width = args.width
    height = args.height
    position = args.position
    border = args.border
    overwrite = args.overwrite

    final_image_dims_dict = DimensionsDict(width=width, height=height)

    process_and_move(
        source_path=input_file_path,
        dimensions_dict=final_image_dims_dict,
        position=position,
        border=border,
        is_overwritable=overwrite,
    )


if __name__ == "__main__":
    main()
