import healpy as hp
import numpy as np
import open3d as o3d
from matplotlib import colormaps

# === Load and Downsample Planck 143 GHz Intensity Map ===
filename = 'HFI_SkyMap_143-field-IQU_2048_R3.00_full.fits'
data = hp.read_map(filename, field=0)

# === Downsample HEALPix map ===
nside = 64
data = hp.ud_grade(data, nside_out=nside)

# === Get pixel directions ===
npix = hp.nside2npix(nside)
pixels = np.arange(npix)
theta, phi = hp.pix2ang(nside, pixels)

# === Convert to Cartesian (unit vectors) ===
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)
directions = np.vstack((x, y, z)).T

# === Normalize intensity (Z-score + gamma) ===
weights = np.nan_to_num(data)
weights = (weights - np.mean(weights)) / np.std(weights)
weights = np.clip(weights, -3, 3)
weights = (weights + 3) / 6
weights = weights ** 0.4

# === Create volume inward ===
n_depth = 5
radii = np.linspace(1.0, 0.1, n_depth)
volume_points = []
volume_colors = []

# Use matplotlib colormap
cmap = colormaps["plasma"]  # or "viridis", "coolwarm", etc.

for r in radii:
    shell = directions * r
    volume_points.append(shell.astype(np.float32))

    # Apply color map
    color_mapped = cmap(weights * (r ** 2))[:, :3]  # RGB only
    volume_colors.append(color_mapped.astype(np.float32))

# === Combine all into point cloud ===
points = np.concatenate(volume_points, axis=0)
colors = np.concatenate(volume_colors, axis=0)

# === Visualize in Open3D ===
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)
o3d.visualization.draw_geometries([pcd])
