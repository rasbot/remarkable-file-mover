import argparse
import os

from PIL import Image
from typing import Literal


def get_processed_output_path(input_path: str, appended_txt: str = "_processed") -> str:
    """Get the output path of a path string by appending a string to the
    file name.

    Ex: "my_dir/my_other_dir/my_file.txt" -> "my_dir/my_other_dir/my_file_processed.txt"

    Args:
        input_path (str): Full path string.
        appended_txt (str, optional): Text to append to file name.
            Defaults to "_processed".

    Returns:
        str: output path string with appended text.
    """
    base, ext = os.path.splitext(input_path)
    return f"{base}{appended_txt}{ext}"


def add_border(
    image: Image, border_width: int, target_width: int, target_height: int
) -> Image:
    """Add a white border to a resized / processed image. The `border_width` will
    be the same for the height and with border lines.

    Args:
        image (Image): PIL Image that has been resized / processed.
        border_width (int): Width of border in pixels.
        target_width (int): Target width of the final image.
        target_height (int): Target height of the final image.

    Returns:
        Image: Resized / processed image with a white border.
    """
    # Do not add a border if it is not > 0
    if border_width <= 0:
        return image

    # Create new image with target dimensions
    bordered = Image.new("RGB", (target_width, target_height), "white")

    # Calculate position to paste the image (these are the same values)
    x = border_width
    y = border_width

    # Paste the image
    bordered.paste(image, (x, y))

    return bordered


def crop_image(
    image_path: str,
    target_width: int,
    target_height: int,
    crop_position: Literal["center", "left", "right", "top", "bottom"] = "center",
    border_width: int = None,
) -> Image:
    """Crop an image to the ratio of the target dimensions.
    Uses the border width to get the right dimensions. Can pass `crop_position`
    to determine what part of the image kept in the final crop.

    Ex: `crop_position` = "center" will crop the height / width relative to the center
    of the image.
    `crop_position` = "left" will crop the image with respect to the leftmost part
    of the image.
    Etc...

    Args:
        image_path (str): Full path to image file.
        target_width (int): Target height of the final image.
        target_height (int): Target width of the final image.
        crop_position (Literal["center", "left", "right", "top", "bottom"], optional): Determine
            where to crop the image relative to.
            Defaults to "center".
        border_width (int, optional): Width of the border.
            Defaults to None.

    Returns:
        Image: Cropped image.
    """
    img = Image.open(image_path)

    # Convert to RGB if necessary (handles PNG with transparency)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # If border is specified, adjust target dimensions for initial resize
    if border_width is not None:
        resize_width = target_width - (2 * border_width)
        resize_height = target_height - (2 * border_width)
    else:
        resize_width = target_width
        resize_height = target_height

    # Calculate target aspect ratio
    target_ratio = resize_width / resize_height

    # Calculate current image aspect ratio
    width, height = img.size
    current_ratio = width / height

    # Calculate dimensions for cropping
    if current_ratio > target_ratio:
        # Image is wider than target ratio
        new_width = int(height * target_ratio)
        new_height = height
        # Calculate crop position
        if crop_position == "left":
            left = 0
        elif crop_position == "right":
            left = width - new_width
        else:  # center
            left = (width - new_width) // 2
        top = 0
        right = left + new_width
        bottom = height
    else:
        # Image is taller than target ratio
        new_width = width
        new_height = int(width / target_ratio)
        left = 0
        # Calculate crop position
        if crop_position == "top":
            top = 0
        elif crop_position == "bottom":
            top = height - new_height
        else:  # center
            top = (height - new_height) // 2
        right = width
        bottom = top + new_height

    # Crop the image
    cropped = img.crop((left, top, right, bottom))

    return cropped


def main():
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

    args = parser.parse_args()
    input_file_path = args.source
    width = args.width
    height = args.height
    position = args.position
    border = args.border


if __name__ == "__main__":
    main()
