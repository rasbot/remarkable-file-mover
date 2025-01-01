"""Process an image to set dimension by cropping, resizing, and adding an optional border."""

import argparse
import os
from enum import Enum
from pathlib import Path
from typing import Dict, Literal, TypedDict

from PIL import Image as PILImage

import src.constants as c
import src.utils as u


class DimensionsDict(TypedDict):
    """DimensionsDict class.

    Args:
        TypedDict (Dict): Width and height of final dimensions.
    """

    width: int
    height: int


class CoordinateDict(TypedDict):
    """CoordinateDict class.

    Args:
        TypedDict (Dict): x and y positions.
    """

    x: int
    y: int


class TextPosition(Enum):
    """Text Position enum.

    Args:
        Enum (str): Text position.
    """

    UPPER_LEFT = "upper_left"
    UPPER_RIGHT = "upper_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_RIGHT = "middle_right"
    LOWER_LEFT = "lower_left"
    LOWER_RIGHT = "lower_right"


def load_image(image_path: Path) -> PILImage:
    """Load a PILImage from a path.

    Args:
        image_path (Path): Path of image file.

    Returns:
        PILImage: Image array.
    """
    return PILImage.open(image_path)


def get_processed_output_path(
    input_path: Path, appended_txt: str = "_processed"
) -> Path:
    """Get the output path of a path string by appending a string to the
    file name.

    Ex: "my_dir/my_other_dir/my_file.txt" -> "my_dir/my_other_dir/my_file_processed.txt"

    Args:
        input_path (Path): Full path string.
        appended_txt (str, optional): Text to append to file name.
            Defaults to "_processed".

    Returns:
        Path: output path string with appended text.
    """
    if isinstance(input_path, str):
        input_path = Path(input_path)
    return input_path.with_name(input_path.stem + appended_txt + input_path.suffix)


def add_border(
    image: PILImage, border_width: int, final_image_dims: DimensionsDict
) -> PILImage:
    """Add a white border to a resized / processed image. The `border_width` will
    be the same for the height and with border lines.

    Args:
        image (PILImage): PIL Image that has been resized / processed.
        border_width (int): Width of border in pixels.
        final_image_dims (DimensionsDict): Final image dimensions dict.

    Returns:
        Image: Resized / processed image with a white border.
    """
    # Do not add a border if it is not > 0
    if border_width <= 0:
        return image

    # Create new image with target dimensions
    bordered = PILImage.new(
        "RGB", (final_image_dims["width"], final_image_dims["height"]), "white"
    )

    # Calculate position to paste the image (these are the same values)
    x_value = border_width
    y_value = border_width

    # Paste the image
    bordered.paste(image, (x_value, y_value))

    return bordered


def get_dimensions(
    image_dims: DimensionsDict,
    border_width: int = None,
) -> DimensionsDict:
    """Get image dimenions for image depending on if a border is
    being added.

    Args:
        image_dims (DimensionsDict): Image dimension dict.
        border_width (int, optional): Border width.
            Defaults to None.

    Returns:
        DimensionsDict: Dict of "width" and "height" values.
    """
    # If border is specified, adjust target dimensions for initial resize
    if border_width is not None:
        resize_width = image_dims["width"] - (2 * border_width)
        resize_height = image_dims["height"] - (2 * border_width)
    else:
        resize_width = image_dims["width"]
        resize_height = image_dims["height"]
    return DimensionsDict(width=resize_width, height=resize_height)


def get_text_position(
    background_image_dims: DimensionsDict,
    text_image_dims: DimensionsDict,
    position: TextPosition,
    side_buffer: int = 0,
) -> CoordinateDict:
    """Get x and y coords for text overlay relative to desired
    position on background image.

    Args:
        background_image_dims (DimensionsDict): Background image dimensions
            dict.
        text_image_dims (DimensionsDict): Text image dimensions dict.
        position (TextPosition): TextPosition enum.
        side_buffer (int, optional): Buffer from the side in pixels. For left positions, moves image right.
            For right positions, moves image left. Defaults to 0.

    Returns:
       CoordinateDict: x, y coords for pasting text overlay.
    """
    # For left positions, x = buffer
    # For right positions, x = background_width - text_width - buffer
    x_left = side_buffer
    x_right = background_image_dims["width"] - text_image_dims["width"] - side_buffer

    y_upper = 0
    y_middle = (background_image_dims["height"] - text_image_dims["height"]) // 2
    y_lower = background_image_dims["height"] - text_image_dims["height"]

    position_coords = {
        TextPosition.UPPER_LEFT: CoordinateDict(x=x_left, y=y_upper),
        TextPosition.UPPER_RIGHT: CoordinateDict(x=x_right, y=y_upper),
        TextPosition.MIDDLE_LEFT: CoordinateDict(x=x_left, y=y_middle),
        TextPosition.MIDDLE_RIGHT: CoordinateDict(x=x_right, y=y_middle),
        TextPosition.LOWER_LEFT: CoordinateDict(x=x_left, y=y_lower),
        TextPosition.LOWER_RIGHT: CoordinateDict(x=x_right, y=y_lower),
    }

    return position_coords[position]


def overlay_text_image(
    processed_img: PILImage,
    text_img: PILImage,
    position: TextPosition,
    img_config: Dict[str, int],
) -> PILImage:
    """Overlay text image onto a background image in the specified
    position.

    Args:
        processed_img (PILImage): Processed image object to add text to.
        text_img (PILImage): Text overlay image (PNG with transparency)
        position (TextPosition): Position to place text from TextPosition enum.
        img_config (Dict[str, int]): Image config dict.

    Returns:
        PIL Image with text overlaid.
    """
    # Verify dimensions
    processed_width = img_config["target_img_dims"]["width"]
    processed_height = img_config["target_img_dims"]["height"]
    if processed_img.size != (processed_width, processed_height):
        raise ValueError(
            f"Background image must be {processed_width}x{processed_height}"
        )
    text_width = img_config["text_overlay_img_dims"]["width"]
    text_height = img_config["text_overlay_img_dims"]["height"]
    if text_img.size != (text_width, text_height):
        raise ValueError(f"Text overlay must be {text_width}x{text_height}")

    background_dims_dict = DimensionsDict(
        width=processed_img.size[0], height=processed_img.size[1]
    )
    text_dims_dict = DimensionsDict(width=text_img.size[0], height=text_img.size[1])

    # Get position coordinates
    coord_dict = get_text_position(
        background_image_dims=background_dims_dict,
        text_image_dims=text_dims_dict,
        position=position,
        side_buffer=img_config["text_img_buffer"],
    )

    # Get alpha channel for mask
    alpha_mask = text_img.split()[3]

    # Create a copy of background to modify
    result = processed_img.copy()

    # Paste text overlay
    result.paste(text_img, (coord_dict["x"], coord_dict["y"]), mask=alpha_mask)

    return result


def crop_image(
    img: PILImage,
    resized_dimensions_dict: DimensionsDict,
    crop_position: Literal["center", "left", "right", "top", "bottom"] = "center",
) -> PILImage:
    """Crop an image to the ratio of the target dimensions.
    Uses the border width to get the right dimensions. Can pass `crop_position`
    to determine what part of the image kept in the final crop.

    Ex: `crop_position` = "center" will crop the height / width relative to the center
    of the image.
    `crop_position` = "left" will crop the image with respect to the leftmost part
    of the image.
    Etc...

    Args:
        img (PILImage): PILImage object.
        resized_dimensions_dict (DimensionsDict): Dict of resized width and height.
        crop_position (Literal["center", "left", "right", "top", "bottom"], optional): Determine
            where to crop the image relative to.
            Defaults to "center".

    Returns:
        PILImage: Cropped image.
    """
    # Calculate resized aspect ratio
    resized_target_ratio = (
        resized_dimensions_dict["width"] / resized_dimensions_dict["height"]
    )

    # Calculate current image aspect ratio
    width, height = img.size
    current_ratio = width / height

    # Calculate dimensions for cropping
    if current_ratio > resized_target_ratio:
        # Image is wider than target ratio
        new_width = int(height * resized_target_ratio)
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
        new_height = int(width / resized_target_ratio)
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


def resize_image(cropped_img: PILImage, resized_dim_dict: DimensionsDict) -> PILImage:
    """Resize the image to the intended final dimensions.

    Args:
        cropped_img (PILImage): Cropped Image.
        resized_dim_dict (DimensionsDict): Dict with resized width and height.

    Returns:
        PILImage: Resized image.
    """
    return cropped_img.resize(
        (resized_dim_dict["width"], resized_dim_dict["height"]),
        PILImage.Resampling.LANCZOS,
    )


def save_image(processed_img: PILImage, output_path: Path) -> None:
    """Save the processed image.

    Args:
        processed_img (PILImage): Processed image.
        output_path (Path): File path to save file to.
    """
    processed_img.save(output_path)
    print(f"Successfully processed image: {output_path}")


def process_image(
    image_path: Path,
    final_image_dims: DimensionsDict,
    img_config: Dict[str, int],
    crop_position: Literal["center", "left", "right", "top", "bottom"] = "center",
    border_width: int = None,
    save_path: Path = None,
    text_image_path: Path = None,
) -> PILImage:
    """Process image by cropping it, resizing it, and adding an optional white border.

    Args:
        image_path (Path): Full path to image file.
        final_image_dims (DimensionsDict): Final image dimensions dict.
        crop_position (Literal["center", "left", "right", "top", "bottom"], optional): Determine
            where to crop the image relative to. Defaults to "center".
        border_width (int, optional): Width of border.
            Defaults to None.
        save_path (Path, optional): Save path for file.
            Defaults to None.
        text_image_path (Path, optional): Path to text overlay file.
            Defaults to None.
        img_config (Dict[str, int]): Image config values.

    Returns:
        PILImage: Fully processed image.
    """
    resized_dim_dict = get_dimensions(
        image_dims=final_image_dims,
        border_width=border_width,
    )
    img = load_image(image_path=image_path)
    cropped_img = crop_image(
        img=img,
        resized_dimensions_dict=resized_dim_dict,
        crop_position=crop_position,
    )

    processed_img = resize_image(
        cropped_img=cropped_img, resized_dim_dict=resized_dim_dict
    )

    if border_width is not None:

        processed_img = add_border(
            image=processed_img,
            border_width=border_width,
            final_image_dims=final_image_dims,
        )
    text_dim_dict = DimensionsDict(
        width=img_config["text_overlay_img_dims"]["width"],
        height=img_config["text_overlay_img_dims"]["height"],
    )
    if text_image_path:
        # load the text image
        text_img = load_image(text_image_path).convert("RGBA")
        text_img = crop_image(img=text_img, resized_dimensions_dict=text_dim_dict)
        text_img = resize_image(cropped_img=text_img, resized_dim_dict=text_dim_dict)

        processed_img = overlay_text_image(
            processed_img=processed_img,
            text_img=text_img,
            position=TextPosition.LOWER_RIGHT,
            img_config=img_config,
        )

    if not save_path:
        save_path = get_processed_output_path(input_path=image_path)

    save_image(processed_img=processed_img, output_path=save_path)


def main():
    """Main function of the script."""
    parser = argparse.ArgumentParser(
        description="Crop and resize an image to specific dimensions."
    )
    parser.add_argument(
        "--source", "-s", type=str, help="Path to input image", required=True
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
        "--textfile",
        "-t",
        nargs="?",
        type=str,
        const="text_overlay.png",
        help="File name of text overlay file, if used.",
    )

    args = parser.parse_args()
    input_file_path = Path(args.source)
    position = args.position
    border = args.border
    text_overlay_filename = args.textfile

    text_overlay_filepath = None
    if text_overlay_filename:
        text_overlay_filepath = os.path.join(
            c.TEXT_OVERLAY_IMAGE_DIR, text_overlay_filename
        )

    img_config = u.load_config_yaml(c.IMAGE_CONFIG_PATH)
    width = img_config["target_img_dims"]["width"]
    height = img_config["target_img_dims"]["height"]

    if width <= 0 or height <= 0:
        raise ValueError(
            f"Target dimensions must be positive integers. Got {width} width and {height} height."
        )

    final_image_dims_dict = DimensionsDict(width=width, height=height)

    process_image(
        image_path=input_file_path,
        final_image_dims=final_image_dims_dict,
        img_config=img_config,
        crop_position=position,
        border_width=border,
        text_image_path=text_overlay_filepath,
    )


if __name__ == "__main__":
    main()
