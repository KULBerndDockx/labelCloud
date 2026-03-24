import json
import glob
import os

labels_dir = "labels"

def convert_labelcloud_json_to_txt(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    lines = []

    for obj in data["objects"]:
        x = obj["centroid"]["x"]
        y = obj["centroid"]["y"]
        z = obj["centroid"]["z"]

        dx = obj["dimensions"]["length"]
        dy = obj["dimensions"]["width"]
        dz = obj["dimensions"]["height"]

        heading = obj["rotations"]["z"]
        category = obj["name"]

        line = f"{x} {y} {z} {dx} {dy} {dz} {heading} {category}"
        lines.append(line)

    with open(output_path, "w") as f:
        for line in lines:
            f.write(line + "\n")

json_files = glob.glob(os.path.join(labels_dir, "*.json"))
converted = 0
skipped = 0
for json_path in json_files:
    if os.path.basename(json_path) == "_classes.json":
        continue
    with open(json_path, 'r') as f:
        data = json.load(f)
    if not data.get("objects"):
        skipped += 1
        continue
    output_path = json_path.replace(".json", ".txt")
    convert_labelcloud_json_to_txt(json_path, output_path)
    converted += 1
    print(f"Converted: {json_path} -> {output_path}")

print(f"Done. Converted {converted} files, skipped {skipped} (no objects).")