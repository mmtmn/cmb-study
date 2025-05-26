import healpy as hp
import numpy as np
from matplotlib import cm
import open3d as o3d

# === CONFIG ===
nside = 64  # Source map resolution (low to moderate)
n_samples = 200_000  # Number of volumetric particles to sample
filename = 'HFI_SkyMap_143-field-IQU_2048_R3.00_full.fits'

# === Load and Downsample Map ===
cmb_map = hp.read_map(filename, field=0)
cmb_map = hp.ud_grade(cmb_map, nside_out=nside)
npix = hp.nside2npix(nside)

# === Generate Volumetric Sample Points (Inside Sphere) ===
# Uniform distribution in volume: r ∈ [0,1]^3 with bias correction
u = np.random.uniform(0, 1, n_samples)
costheta = np.random.uniform(-1, 1, n_samples)
phi = np.random.uniform(0, 2 * np.pi, n_samples)
r = u ** (1/3)  # bias correction to ensure uniform density

theta = np.arccos(costheta)
x = r * np.sin(theta) * np.cos(phi)
y = r * np.sin(theta) * np.sin(phi)
z = r * np.cos(theta)
points = np.vstack((x, y, z)).T

# === Map Each Point to a HEALPix Pixel ===
# (project point back to unit sphere for angular position)
vec = points / np.linalg.norm(points, axis=1)[:, np.newaxis]
pix = hp.vec2pix(nside, vec[:, 0], vec[:, 1], vec[:, 2])
weights = cmb_map[pix]

# === Normalize & Apply Color Map ===
weights = np.nan_to_num(weights)
mean, std = np.mean(weights), np.std(weights)
weights = (weights - mean) / std
weights = np.clip(weights, -3, 3)
weights = (weights + 3) / 6
weights = weights ** 0.4  # optional gamma boost

# False-color using matplotlib colormap
cmap = cm.get_cmap("coolwarm")
colors = cmap(weights)[:, :3]

# === Create and Visualize Point Cloud ===
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)

print(f"Generated {n_samples} volumetric particles.")
o3d.visualization.draw_geometries([pcd])
