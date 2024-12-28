import argparse
import os

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
