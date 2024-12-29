from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT_DIR / "remarkable_config.txt"
print(CONFIG_PATH)
