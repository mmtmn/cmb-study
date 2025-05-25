import healpy as hp
import numpy as np
import open3d as o3d

# === Load Planck 143 GHz HEALPix FITS Map ===
filename = 'HFI_SkyMap_143-field-IQU_2048_R3.00_full.fits'  # <-- Make sure this matches your file
data = hp.read_map(filename)

# === Get NSIDE and total pixel count ===
nside = hp.npix2nside(len(data))
npix = hp.nside2npix(nside)
pixels = np.arange(npix)

# === Angular coordinates (theta: [0, pi], phi: [0, 2pi]) ===
theta, phi = hp.pix2ang(nside, pixels)

# === Convert spherical to Cartesian coordinates ===
x = np.sin(theta) * np.cos(phi)
y = np.sin(theta) * np.sin(phi)
z = np.cos(theta)

# === Clean + Normalize intensity data ===
weights = np.nan_to_num(data)

# Optional: Log scaling to bring out subtle structure
weights = np.log1p(np.abs(weights))  # log(1 + |x|)

# Normalize weights to [0, 1] for color mapping
weights = (weights - np.min(weights)) / (np.max(weights) - np.min(weights))

# === Build 3D Point Cloud on Unit Sphere ===
points = np.vstack((x, y, z)).T
colors = np.vstack([weights]*3).T  # Grayscale color

# === Create and Display Point Cloud ===
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)

o3d.visualization.draw_geometries([pcd])
