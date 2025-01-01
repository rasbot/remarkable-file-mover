"""Constants script"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT_DIR / "config" / "remarkable_config.txt"
TEXT_OVERLAY_IMAGE_DIR = ROOT_DIR / "text_overlay_images"

TARGET_IMG_DIMS = {"width": 1620, "height": 2160}
TEXT_OVERLAY_IMG_DIMS = {"width": 810, "height": 720}
TEXT_IMG_BUFFER = 150
