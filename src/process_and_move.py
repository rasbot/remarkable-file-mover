import argparse

from src.constants import CONFIG_PATH
from src.crop_resize import get_processed_output_path, process_image
from src.move_file import get_destination_path, move_file


def process_and_move(
    source_path: str,
    width: int,
    height: int,
    position: str,
    border: int,
):
    processed_path = get_processed_output_path(input_path=source_path)
    process_image(
        image_path=source_path,
        target_width=width,
        target_height=height,
        crop_position=position,
        border_width=border,
        save_path=processed_path,
    )
    destination_path = get_destination_path(config_path=CONFIG_PATH)
    move_file(source_path=processed_path, destination_path=destination_path)


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

    process_and_move(
        source_path=input_file_path,
        width=width,
        height=height,
        position=position,
        border=border,
    )


if __name__ == "__main__":
    main()
