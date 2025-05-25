import healpy as hp
import numpy as np
import open3d as o3d

# === Load HEALPix FITS Map ===
filename = 'HFI_SkyMap_857-field-Int_2048_R3.00_full.fits'
data = hp.read_map(filename)

# === Get NSIDE and Pixel Info ===
nside = hp.npix2nside(len(data))
pixels = np.arange(hp.nside2npix(nside))

# === Get Angular Coordinates ===
theta, phi = hp.pix2ang(nside, pixels)

# === Convert to 3D Cartesian Coordinates on Unit Sphere ===
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

# === Normalize and Clean Weights (Intensity Values) ===
weights = np.nan_to_num(data)
weights = (weights - np.min(weights)) / (np.max(weights) - np.min(weights))  # Scale 0–1

# === Optional Filter: Remove Near-Zero Weights ===
mask = weights > 0.01
x, y, z, weights = x[mask], y[mask], z[mask], weights[mask]

# === Create Point Cloud on Unit Sphere ===
points = np.vstack((x, y, z)).T

# === Color by Normalized Weight (Grayscale) ===
colors = np.vstack([weights]*3).T  # Repeat weights for R, G, B

# === Create and Visualize Point Cloud ===
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)

o3d.visualization.draw_geometries([pcd])
