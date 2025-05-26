import healpy as hp
import numpy as np
import open3d as o3d

# === File paths ===
file_r = 'HFI_SkyMap_857-field-Int_2048_R3.00_full.fits'  # Dust
file_g = 'HFI_SkyMap_545-field-Int_2048_R3.00_full.fits'  # Synchrotron
file_b = 'HFI_SkyMap_143-field-IQU_2048_R3.00_full.fits'  # CMB

# === Parameters ===
nside = 64
n_depth = 5
radii = np.linspace(1.0, 0.1, n_depth)

# === Load and downsample maps ===
print("Loading maps...")
map_r = hp.ud_grade(hp.read_map(file_r), nside_out=nside)
map_g = hp.ud_grade(hp.read_map(file_g), nside_out=nside)
map_b = hp.ud_grade(hp.read_map(file_b, field=0), nside_out=nside)

# === Convert to HEALPix directions ===
npix = hp.nside2npix(nside)
theta, phi = hp.pix2ang(nside, np.arange(npix))
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)
directions = np.vstack((x, y, z)).T

# === Stack and globally normalize RGB ===
print("Stacking and normalizing RGB...")
rgb_raw = np.stack([map_r, map_g, map_b], axis=1)
rgb_raw = np.nan_to_num(rgb_raw)
rgb_raw = np.clip(rgb_raw, np.percentile(rgb_raw, 1), np.percentile(rgb_raw, 99))  # Remove outliers

# Normalize across all channels together
rgb_min = rgb_raw.min()
rgb_max = rgb_raw.max()
rgb = (rgb_raw - rgb_min) / (rgb_max - rgb_min)
rgb = np.clip(rgb, 0, 1).astype(np.float32)

# === Generate radial holographic volume ===
volume_points = []
volume_colors = []

for r in radii:
    shell = directions * r
    volume_points.append(shell.astype(np.float32))
    faded_rgb = rgb * (r ** 1.5)
    volume_colors.append(np.clip(faded_rgb, 0, 1).astype(np.float32))

points = np.concatenate(volume_points, axis=0)
colors = np.concatenate(volume_colors, axis=0)

# === Visualize ===
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)

print("Rendering full RGB holographic universe...")
o3d.visualization.draw_geometries([pcd])
