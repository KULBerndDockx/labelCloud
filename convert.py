import os
import numpy as np

def pcd_to_npy(pcd_path, npy_path):
    with open(pcd_path, 'r') as f:
        lines = f.readlines()

    # Find where DATA starts
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("DATA"):
            data_start = i + 1
            break

    # Load numeric data
    data = np.loadtxt(lines[data_start:])

    # Extract x, y, z, intensity (columns 0,1,2,3)
    points = data[:, :4].astype(np.float32)

    np.save(npy_path, points)


pcd_folder = r"C:\Users\bernd\OneDrive\NU\Main-Quest\Masterproef\LabelCloud\2025-11-18-13-51-31"
npy_folder = "npy"

os.makedirs(npy_folder, exist_ok=True)

for file in sorted(os.listdir(pcd_folder)):
    if file.endswith(".pcd"):
        pcd_path = os.path.join(pcd_folder, file)
        npy_path = os.path.join(npy_folder, file.replace(".pcd", ".npy"))
        pcd_to_npy(pcd_path, npy_path)