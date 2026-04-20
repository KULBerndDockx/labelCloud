from __future__ import annotations

import argparse
import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple


INPUT_FOLDER = Path("labels")
OUTPUT_FOLDER = Path("new_labels")
DEFAULT_START = 175
DEFAULT_END = 400


def build_logger(output_folder: Path) -> logging.Logger:
    output_folder.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("fix_labels")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(output_folder / "fix_labels.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(file_handler)

    return logger


def is_numeric_label_file(path: Path) -> bool:
    return path.suffix.lower() == ".json" and path.name != "_classes.json" and path.stem.isdigit()


def within_range(path: Path, start: int, end: int) -> bool:
    if not is_numeric_label_file(path):
        return False
    file_number = int(path.stem)
    return start <= file_number <= end


def swap_length_width(obj: Dict[str, Any]) -> None:
    dimensions = obj["dimensions"]
    dimensions["length"], dimensions["width"] = dimensions["width"], dimensions["length"]


def rotate_object(obj: Dict[str, Any], z_rotation: float) -> None:
    obj["rotations"]["z"] = z_rotation


def fix_car_or_cyclist(obj: Dict[str, Any]) -> bool:
    dimensions = obj["dimensions"]
    length = dimensions["length"]
    width = dimensions["width"]

    if width > length:
        swap_length_width(obj)
        rotate_object(obj, 270.0)
        return True
    return False


def fix_pedestrians(objects: List[Dict[str, Any]], filename: str, logger: logging.Logger) -> int:
    pedestrian_indices = [index for index, obj in enumerate(objects) if obj.get("name") == "Pedestrian"]

    if len(pedestrian_indices) == 1:
        logger.info(f"{filename}: one pedestrian found, left unchanged for manual review")
        return 0

    if len(pedestrian_indices) < 2:
        return 0

    ordered_indices = sorted(
        pedestrian_indices,
        key=lambda index: (objects[index]["centroid"]["y"], index),
    )

    lowest_index = ordered_indices[0]
    highest_index = ordered_indices[-1]

    changed = 0

    swap_length_width(objects[lowest_index])
    rotate_object(objects[lowest_index], 90.0)
    changed += 1

    if highest_index != lowest_index:
        swap_length_width(objects[highest_index])
        rotate_object(objects[highest_index], 270.0)
        changed += 1

    if len(pedestrian_indices) > 2:
        logger.info(
            f"{filename}: {len(pedestrian_indices)} pedestrians found, only lowest/highest were adjusted"
        )

    return changed


def process_file(input_path: Path, output_path: Path, logger: logging.Logger, start: int, end: int) -> Tuple[int, int]:
    if input_path.name == "_classes.json" or input_path.suffix.lower() != ".json":
        shutil.copy2(input_path, output_path)
        return 0, 0

    with input_path.open("r", encoding="utf-8") as read_file:
        data = json.load(read_file)

    if not within_range(input_path, start, end):
        shutil.copy2(input_path, output_path)
        return 0, 0

    changed_objects = 0
    objects = data.get("objects", [])

    for obj in objects:
        name = obj.get("name")
        if name in {"Car", "Cyclist"}:
            if fix_car_or_cyclist(obj):
                changed_objects += 1

    changed_objects += fix_pedestrians(objects, input_path.name, logger)

    if changed_objects == 0:
        shutil.copy2(input_path, output_path)
        return 0, len(objects)

    with output_path.open("w", encoding="utf-8") as write_file:
        json.dump(data, write_file, indent="\t", ensure_ascii=False)

    return changed_objects, len(objects)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix rotated LabelCloud JSON labels and write them to a new folder.")
    parser.add_argument("--input", type=Path, default=INPUT_FOLDER, help="Folder with the original label JSON files")
    parser.add_argument("--output", type=Path, default=OUTPUT_FOLDER, help="Folder where corrected labels are written")
    parser.add_argument("--start", type=int, default=DEFAULT_START, help="First numeric label file to fix")
    parser.add_argument("--end", type=int, default=DEFAULT_END, help="Last numeric label file to fix")
    args = parser.parse_args()

    logger = build_logger(args.output)

    if not args.input.is_dir():
        raise FileNotFoundError(f"Input folder does not exist: {args.input}")

    args.output.mkdir(parents=True, exist_ok=True)

    processed_files = 0
    changed_files = 0
    changed_objects = 0

    for input_path in sorted(args.input.iterdir()):
        if not input_path.is_file():
            continue

        output_path = args.output / input_path.name
        file_changes, _ = process_file(input_path, output_path, logger, args.start, args.end)
        processed_files += 1
        if file_changes:
            changed_files += 1
            changed_objects += file_changes

    logger.info(
        f"Done. Processed {processed_files} files, changed {changed_objects} objects in {changed_files} files."
    )


if __name__ == "__main__":
    main()