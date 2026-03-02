import json
json_path = "labels/2025-11-18-13-51-31_Velodyne-VLP-16-Data (Frame 196).json"
output_path = "labels/2025-11-18-13-51-31_Velodyne-VLP-16-Data (Frame 196).txt"
def convert_labelcloud_json_to_txt(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    lines = []

    for obj in data["objects"]:
        x = obj["centroid"]["x"]
        y = obj["centroid"]["y"]
        z = obj["centroid"]["z"]

        # IMPORTANT: swap length/width
        dx = obj["dimensions"]["width"]   # likely true length
        dy = obj["dimensions"]["length"]  # likely true width
        dz = obj["dimensions"]["height"]

        heading = obj["rotations"]["z"]
        category = obj["name"]

        line = f"{x} {y} {z} {dx} {dy} {dz} {heading} {category}"
        lines.append(line)

    with open(output_path, "w") as f:
        for line in lines:
            f.write(line + "\n")

convert_labelcloud_json_to_txt(json_path, output_path)