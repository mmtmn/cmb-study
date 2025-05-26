# WARNING: this script will generate a 25GB dataset to be runned by the CUDA script

import healpy as hp
import numpy as np

# === Output filename ===
output_file = "full_cloud.txt"

# === Load Planck 143 GHz map ===
filename = 'HFI_SkyMap_143-field-IQU_2048_R3.00_full.fits'
nside = 2048                # Full-resolution: ~50 million directions
n_depth = 10                # Number of radial samples
radii = np.linspace(1.0, 0.1, n_depth)

print("Loading and processing CMB map...")
cmb_map = hp.read_map(filename, field=0)
cmb_map = np.nan_to_num(cmb_map)

# === Normalize intensities ===
weights = (cmb_map - np.mean(cmb_map)) / np.std(cmb_map)
weights = np.clip(weights, -3, 3)
weights = (weights + 3) / 6
weights = weights ** 0.4  # Gamma corrected

# === Get HEALPix directions ===
pixels = np.arange(hp.nside2npix(nside))
theta, phi = hp.pix2ang(nside, pixels)
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)
directions = np.vstack((x, y, z)).T.astype(np.float32)

# === Build full holographic volume ===
volume_points = []
volume_colors = []

print("Generating holographic volume...")

for r in radii:
    shell = directions * r
    faded_weights = weights * (r ** 2)
    colors = np.clip(np.vstack([faded_weights] * 3).T, 0, 1)

    volume_points.append(shell)
    volume_colors.append(colors.astype(np.float32))

# === Combine all and save ===
points = np.concatenate(volume_points, axis=0)
colors = np.concatenate(volume_colors, axis=0)
cloud_data = np.hstack((points, colors))

print(f"Saving to {output_file} ({len(cloud_data)} points)...")
np.savetxt(output_file, cloud_data, fmt="%.6f")
print("Done.")
