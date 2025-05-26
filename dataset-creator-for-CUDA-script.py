# main.py
import healpy as hp
import numpy as np

# === Output file for CUDA/OpenGL viewer ===
output_file = "full_cloud.npy"

# === Input CMB map ===
filename = 'HFI_SkyMap_143-field-IQU_2048_R3.00_full.fits'
nside = 2048                  # Full map resolution
n_depth = 5
radii = np.linspace(1.0, 0.1, n_depth)

# === Load and process CMB ===
print("Loading and processing CMB map...")
cmb_map = hp.read_map(filename, field=0)
cmb_map = np.nan_to_num(cmb_map)

# === Normalize weights ===
weights = (cmb_map - np.mean(cmb_map)) / np.std(cmb_map)
weights = np.clip(weights, -3, 3)
weights = (weights + 3) / 6
weights = weights ** 0.4

# === Get pixel directions ===
pixels = np.arange(hp.nside2npix(nside))
theta, phi = hp.pix2ang(nside, pixels)
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)
directions = np.vstack((x, y, z)).T.astype(np.float32)

# === Build 3D holographic volume ===
print("Generating volume...")
volume_points = []
volume_colors = []

for r in radii:
    shell = directions * r
    volume_points.append(shell)

    faded = weights * (r ** 2)
    shell_colors = np.clip(np.vstack([faded] * 3).T, 0, 1)
    volume_colors.append(shell_colors.astype(np.float32))

# === Combine and save ===
points = np.concatenate(volume_points, axis=0)
colors = np.concatenate(volume_colors, axis=0)
cloud = np.hstack((points, colors)).astype(np.float32)

print(f"Saving {cloud.shape[0]} points to {output_file}...")
np.save(output_file, cloud)
print("Done. Total size: {:.2f} MB".format(cloud.nbytes / 1e6))
