"""Constants script"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT_DIR / "config"

CONFIG_PATH = CONFIG_DIR / "remarkable_config.txt"
IMAGE_CONFIG_PATH = CONFIG_DIR / "image_config.yaml"
TEXT_OVERLAY_IMAGE_DIR = ROOT_DIR / "text_overlay_images"

IMG_POSITIONS = ["center", "left", "right", "top", "bottom"]

IMG_POSITIONS_HELP = (
    "Position to crop from. Options:\n"
    "  - center\n"
    "  - left\n"
    "  - right\n"
    "  - top\n"
    "  - bottom\n"
    "(default: center)"
)

TEXT_POSITIONS = [
    "upper_left",
    "upper_middle",
    "upper_right",
    "middle_left",
    "middle_middle",
    "middle_right",
    "lower_left",
    "lower_middle",
    "lower_right",
]

TEXT_POSITIONS_HELP = (
    "Position to add text overlay image to. Options:\n"
    "  - upper:  left, middle, right\n"
    "  - middle: left, middle, right\n"
    "  - lower:  left, middle, right\n"
    "Combine with underscore like (upper_left, middle_middle, lower_middle, etc)\n"
    "(default: lower_right)"
)
