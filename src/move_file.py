"""Move a file to a destination and rename it to 'suspended.png'"""

from pathlib import Path
from src.constants import CONFIG_PATH


def get_destination_path(config_path: Path) -> Path:
    """Read in the value of the desitination path from
    the config file (value for `SOURCE_PATH` in config).

    Args:
        config_path (Path): Path to config file.

    Returns:
        Path: Path to move image to.
    """
    with open(config_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    destination_path = None
    for line in lines:
        if line.startswith("SOURCE_PATH="):
            destination_path = line.split("=", 1)[1].strip()

    return Path(destination_path)


print(get_destination_path(CONFIG_PATH))
