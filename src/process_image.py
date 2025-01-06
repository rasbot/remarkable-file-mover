"""Process an image to set dimension by cropping, resizing, and adding an optional border."""

import argparse
from pathlib import Path
from typing import Literal

from PIL import Image as PILImage

from src.utils import (
    CoordinateDict,
    DimensionsDict,
    ProcessConfig,
    TextPosition,
    add_process_image_args,
    get_image_dimensions_from_config,
    load_image_config,
    update_processconfig_from_args,
)


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
    image_position_buffer: int = 0,
) -> CoordinateDict:
    """Get x and y coords for text overlay relative to desired
    position on background image.

    Args:
        background_image_dims (DimensionsDict): Background image dimensions
            dict.
        text_image_dims (DimensionsDict): Text image dimensions dict.
        position (TextPosition): TextPosition enum.
        image_position_buffer (int, optional): Buffer for the image position
            in pixels.
            For left positions, moves image right.
            For right positions, moves image left.
            For upper positions, moves image down.
            For lower positions, moves image up.
            Defaults to 0.

    Returns:
       CoordinateDict: x, y coords for pasting text overlay.
    """
    x_left = image_position_buffer
    x_right = (
        background_image_dims["width"]
        - text_image_dims["width"]
        - image_position_buffer
    )
    # Calculate center x-position
    x_middle = (background_image_dims["width"] - text_image_dims["width"]) // 2

    y_upper_base = 0
    y_middle = (background_image_dims["height"] - text_image_dims["height"]) // 2
    y_lower_base = background_image_dims["height"] - text_image_dims["height"]

    y_upper = y_upper_base + image_position_buffer
    y_lower = y_lower_base - image_position_buffer

    position_coords = {
        TextPosition.UPPER_LEFT: CoordinateDict(x=x_left, y=y_upper),
        TextPosition.UPPER_MIDDLE: CoordinateDict(x=x_middle, y=y_upper),
        TextPosition.UPPER_RIGHT: CoordinateDict(x=x_right, y=y_upper),
        TextPosition.MIDDLE_LEFT: CoordinateDict(x=x_left, y=y_middle),
        TextPosition.MIDDLE_MIDDLE: CoordinateDict(x=x_middle, y=y_middle),
        TextPosition.MIDDLE_RIGHT: CoordinateDict(x=x_right, y=y_middle),
        TextPosition.LOWER_LEFT: CoordinateDict(x=x_left, y=y_lower),
        TextPosition.LOWER_MIDDLE: CoordinateDict(x=x_middle, y=y_lower),
        TextPosition.LOWER_RIGHT: CoordinateDict(x=x_right, y=y_lower),
    }
    return position_coords[position]


def invert_text_color(image: PILImage) -> PILImage:
    """Invert the color of text (black to white or white to black)
    while preserving transparency.

    Args:
        image (PILImage): PIL Image in RGBA mode

    Returns:
        image with inverted colors but same transparency.
    """
    # Split into RGBA channels
    r, g, b, a = image.split()

    # Create inverted RGB channels (255 - original)
    r_inv = PILImage.eval(r, lambda x: 255 - x)
    g_inv = PILImage.eval(g, lambda x: 255 - x)
    b_inv = PILImage.eval(b, lambda x: 255 - x)

    # Merge back together with original alpha
    inverted = PILImage.merge("RGBA", (r_inv, g_inv, b_inv, a))

    return inverted


def overlay_text_image(
    processed_img: PILImage,
    text_img: PILImage,
    position: TextPosition,
    image_buffer: int,
) -> PILImage:
    """Overlay text image onto a background image in the specified
    position.

    Args:
        processed_img (PILImage): Processed image object to add text to.
        text_img (PILImage): Text overlay image (PNG with transparency)
        position (TextPosition): Position to place text from TextPosition enum.
        image_buffer (int): buffer in pixels for image padding.

    Returns:
        PIL Image with text overlaid.
    """
    print("DEBUG:", position)
    background_dims_dict = DimensionsDict(
        width=processed_img.size[0], height=processed_img.size[1]
    )
    text_dims_dict = DimensionsDict(width=text_img.size[0], height=text_img.size[1])

    # Get position coordinates
    coord_dict = get_text_position(
        background_image_dims=background_dims_dict,
        text_image_dims=text_dims_dict,
        position=position,
        image_position_buffer=image_buffer,
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


def is_image_at_target_dims(
    img: PILImage, target_width: int, target_height: int
) -> bool:
    """Check if an image has the target dimensions.

    Args:
        img (PILImage): Image to check dimensions.
        target_width (int): Target width.
        target_height (int): Target height.

    Returns:
        bool: True if dimensions match, False if either or both do not.
    """
    return img.size == (target_width, target_height)


def process_image(
    process_config: ProcessConfig,
) -> PILImage:
    """Process image by cropping it, resizing it, and adding an optional white border.

    Args:
        process_config (ProcessConfig): ProcessConfig instance.

    Returns:
        PILImage: Fully processed image.
    """
    # unpack dataclass
    final_image_dims = process_config.final_image_dims
    border_width = process_config.border_width
    image_path = process_config.image_path
    crop_position = process_config.crop_position
    img_config = process_config.img_config
    text_image_path = process_config.text_image_path
    save_path = process_config.save_path
    is_inverted = process_config.is_inverted
    image_buffer = process_config.image_buffer
    text_position = process_config.text_position

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

    # target dimensions for text overlay image
    text_img_width, text_img_height = get_image_dimensions_from_config(
        img_config=img_config, img_type="text_overlay"
    )
    text_dim_dict = DimensionsDict(
        width=text_img_width,
        height=text_img_height,
    )
    if text_image_path:
        # load the text image
        text_img = load_image(text_image_path).convert("RGBA")
        if is_inverted:
            text_img = invert_text_color(image=text_img)
        # check image size and only resize if needed
        if not is_image_at_target_dims(
            img=text_img, target_width=text_img_width, target_height=text_img_height
        ):
            print("resizing text overlay image...")
            text_img = crop_image(img=text_img, resized_dimensions_dict=text_dim_dict)
            text_img = resize_image(
                cropped_img=text_img, resized_dim_dict=text_dim_dict
            )

        processed_img = overlay_text_image(
            processed_img=processed_img,
            text_img=text_img,
            position=text_position,
            image_buffer=image_buffer,
        )

    if not save_path:
        save_path = get_processed_output_path(input_path=image_path)

    save_image(processed_img=processed_img, output_path=save_path)


def main():
    """Main function of the script."""
    parser = argparse.ArgumentParser(
        description="Crop and resize an image to specific dimensions.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    add_process_image_args(parser=parser)

    args = parser.parse_args()

    img_config = load_image_config()
    width, height = get_image_dimensions_from_config(
        img_config=img_config, img_type="target"
    )

    process_config = ProcessConfig()
    process_config.final_image_dims = DimensionsDict(width=width, height=height)
    process_config.img_config = img_config
    process_config = update_processconfig_from_args(config=process_config, args=args)
    process_image(process_config=process_config)


if __name__ == "__main__":
    main()
