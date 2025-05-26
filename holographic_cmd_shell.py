import healpy as hp
import numpy as np
import open3d as o3d

# === Load and Downsample Planck 143 GHz Intensity Map ===
filename = 'HFI_SkyMap_143-field-IQU_2048_R3.00_full.fits'
data = hp.read_map(filename, field=0)

# === Downsample HEALPix map to lower resolution ===
nside = 64  # Lower resolution for manageable size (~50k pixels)
data = hp.ud_grade(data, nside_out=nside)

# === Get pixel directions ===
npix = hp.nside2npix(nside)
pixels = np.arange(npix)
theta, phi = hp.pix2ang(nside, pixels)

# === Spherical to Cartesian (unit vectors) ===
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)
directions = np.vstack((x, y, z)).T

# === Normalize CMB intensity to [0, 1] with gamma ===
weights = np.nan_to_num(data)
weights = (weights - np.mean(weights)) / np.std(weights)
weights = np.clip(weights, -3, 3)
weights = (weights + 3) / 6
weights = weights ** 0.4

# === Create 3D volume inward along radial lines ===
n_depth = 5  # Number of samples along each ray
radii = np.linspace(1.0, 0.1, n_depth)  # Outer to inner radius

volume_points = []
volume_colors = []

for r in radii:
    shell = directions * r
    volume_points.append(shell.astype(np.float32))

    faded_weights = weights * (r ** 2)  # fade by square of radius
    shell_colors = np.vstack([faded_weights]*3).T.astype(np.float32)
    volume_colors.append(shell_colors)

# === Combine all points and colors ===
points = np.concatenate(volume_points, axis=0)
colors = np.concatenate(volume_colors, axis=0)

# === Build and display point cloud ===
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)

o3d.visualization.draw_geometries([pcd])
