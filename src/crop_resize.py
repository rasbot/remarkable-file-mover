"""Process an image to set dimension by cropping, resizing, and adding an optional border."""

import argparse
import os
from typing import Dict, Literal

from PIL import Image


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
    image: Image, border_width: int, target_dim_dict: Dict[str, int]
) -> Image:
    """Add a white border to a resized / processed image. The `border_width` will
    be the same for the height and with border lines.

    Args:
        image (Image): PIL Image that has been resized / processed.
        border_width (int): Width of border in pixels.
        targetdim_dict (Dict[str, int]): Target width and height dict.

    Returns:
        Image: Resized / processed image with a white border.
    """
    # Do not add a border if it is not > 0
    if border_width <= 0:
        return image

    # Create new image with target dimensions
    bordered = Image.new(
        "RGB", (target_dim_dict["width"], target_dim_dict["height"]), "white"
    )

    # Calculate position to paste the image (these are the same values)
    x_value = border_width
    y_value = border_width

    # Paste the image
    bordered.paste(image, (x_value, y_value))

    return bordered


def get_resized_dimensions(
    target_width: int,
    target_height: int,
    border_width: int = None,
) -> Dict[str, int]:
    """Get image dimenions for image depending on if a border is
    being added.

    Args:
        target_width (int): Target width.
        target_height (int): Target height.
        border_width (int, optional): Border width.
            Defaults to None.

    Returns:
        Dict[str, int]: Dict of "width" and "height" values.
    """
    # If border is specified, adjust target dimensions for initial resize
    if border_width is not None:
        resize_width = target_width - (2 * border_width)
        resize_height = target_height - (2 * border_width)
    else:
        resize_width = target_width
        resize_height = target_height
    return {"width": resize_width, "height": resize_height}


def crop_image(
    image_path: str,
    target_dimensions_dict: Dict[str, int],
    crop_position: Literal["center", "left", "right", "top", "bottom"] = "center",
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
        target_dimensions_dict (Dict[str, int]): Dict of target width and height.
        crop_position (Literal["center", "left", "right", "top", "bottom"], optional): Determine
            where to crop the image relative to.
            Defaults to "center".

    Returns:
        Image: Cropped image.
    """
    img = Image.open(image_path)

    # Convert to RGB if necessary (handles PNG with transparency)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Calculate target aspect ratio
    target_ratio = target_dimensions_dict["width"] / target_dimensions_dict["height"]

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


def resize_image(cropped_img: Image, target_dim_dict: Dict[str, int]) -> Image:
    """Resize the image to the intended final dimensions.

    Args:
        cropped_img (Image): Cropped Image.
        target_dim_dict (Dict[str, int]): Dict with target width and height.

    Returns:
        Image: Resized image.
    """
    return cropped_img.resize(
        (target_dim_dict["width"], target_dim_dict["height"]), Image.Resampling.LANCZOS
    )


def process_image(
    image_path: str,
    target_width: int,
    target_height: int,
    crop_position: Literal["center", "left", "right", "top", "bottom"] = "center",
    border_width: int = None,
) -> Image:
    """Process image by cropping it, resizing it, and adding an optional white border.

    Args:
        image_path (str): Full path to image file.
        target_width (int): Target width of final image.
        target_height (int): Target height of final image.
        crop_position (Literal["center", "left", "right", "top", "bottom"], optional): Determine
            where to crop the image relative to. Defaults to "center".
        border_width (int, optional): Width of border.
            Defaults to None.

    Returns:
        Image: Fully processed image.
    """
    target_dim_dict = get_resized_dimensions(
        target_width=target_width,
        target_height=target_height,
        border_width=border_width,
    )
    cropped_img = crop_image(
        image_path=image_path,
        target_dimensions_dict=target_dim_dict,
        crop_position=crop_position,
    )

    prcessed_img = resize_image(
        cropped_img=cropped_img, target_dim_dict=target_dim_dict
    )

    if border_width is not None:
        prcessed_img = add_border(
            image=prcessed_img,
            border_width=border_width,
            target_dim_dict=target_dim_dict,
        )

    return prcessed_img


def main():
    """Main function of the script."""
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

    process_image(
        image_path=input_file_path,
        target_width=width,
        target_height=height,
        crop_position=position,
        border_width=border,
    )


if __name__ == "__main__":
    main()
