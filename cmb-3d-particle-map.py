import healpy as hp
import numpy as np
import open3d as o3d

# === Load Planck 143 GHz Intensity Map ===
filename = 'HFI_SkyMap_143-field-IQU_2048_R3.00_full.fits'
data = hp.read_map(filename, field=0)  # field=0 = Intensity (I)

# === HEALPix Resolution Info ===
nside = hp.npix2nside(len(data))
npix = hp.nside2npix(nside)
pixels = np.arange(npix)

# === Spherical to Cartesian Coordinates ===
theta, phi = hp.pix2ang(nside, pixels)
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

# === Normalize CMB Intensity (Z-score + contrast boost) ===
weights = np.nan_to_num(data)
mean = np.mean(weights)
std = np.std(weights)
weights = (weights - mean) / std              # Standardize
weights = np.clip(weights, -3, 3)             # Clip outliers
weights = (weights + 3) / 6                   # Scale to [0, 1]
weights = weights ** 0.4                      # Gamma correction for brightness

# === Create Point Cloud (Unit Sphere) ===
points = np.vstack((x, y, z)).T
colors = np.vstack([weights]*3).T  # Grayscale coloring

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)

# === Visualize ===
o3d.visualization.draw_geometries([pcd])
