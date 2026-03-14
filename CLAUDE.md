# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool for processing images to be used as sleep screens on the reMarkable Paper Pro tablet (1620x2160). The pipeline crops, resizes, optionally adds borders/text overlays, then copies the result to a destination as `suspended.png` for transfer to the device via SSH.

## Setup & Commands

```bash
# Install dependencies (requires Python 3.13+)
pip install -r requirements.txt
pip install -e .

# Run image processing only
python src/process_image.py -s <image_path> [-cp center] [-b 30] [-t text_overlay.png] [-i] [-tp lower_right] [-tb 0]

# Copy processed file to destination
python src/move_file.py -s <image_path> [-o]

# Process and move in one step
python src/process_and_move.py -s <image_path> [same options as process_image + -o]

# Push to device (Windows, requires PuTTY)
./src/push_to_device.bat
```

No test framework or linter is currently configured.

## Architecture

Three-stage pipeline, each stage runnable independently:

1. **`src/process_image.py`** — Image processing: load → crop to aspect ratio → resize (LANCZOS) → optional border → optional text overlay → save as `*_processed.png`
2. **`src/move_file.py`** — Copies processed image to configured destination as `suspended.png`. Overwrite-protected by default (`ProtectedFile` exception).
3. **`src/push_to_device.bat`** — SSH transfer to reMarkable via PuTTY's `plink`/`pscp`.

**`src/process_and_move.py`** orchestrates stages 1+2 together.

### Key supporting modules

- **`src/constants.py`** — Path constants (`ROOT_DIR`, `CONFIG_DIR`, `IMAGE_CONFIG_PATH`, `TEXT_OVERLAY_IMAGE_DIR`) and valid position lists.
- **`src/utils.py`** — Dataclasses (`ProcessConfig`, `MoveConfig`), enums (`TextPosition`, `ConfigKey`), TypedDicts (`DimensionsDict`, `CoordinateDict`), config parsing, argparse helpers, validation functions.

### Configuration

- **`config/image_config.yaml`** — Target image dimensions (1620x2160) and text overlay dimensions (800x375).
- **`config/remarkable_config.txt`** — User-created key=value file with device IP, password, paths. Parsed by `get_config_path()` in utils.
- Text overlay images go in `text_overlay_images/`.

## Conventions

- All source modules live in `src/` and use `from src.` imports (package installed in editable mode).
- Image processing uses Pillow (`PIL`).
- Paths use `pathlib.Path` throughout; `constants.py` derives all paths from `ROOT_DIR`.
- Crop positions: `center`, `left`, `right`, `top`, `bottom`. Text positions: 3x3 grid (`upper_left` through `lower_right`).
