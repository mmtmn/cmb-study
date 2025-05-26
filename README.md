
# using the HFI_SkyMap_857-field-Int_2048_R3.00_full from Plank Lagacy Archive, we get this:

![image](https://github.com/user-attachments/assets/f1f8919e-55cd-4708-964b-4af139a3f416)



# using the HFI_SkyMap_143-field-IQU_2048_R3.00_full from Plank Lagacy Archive, we get this:
![image](https://github.com/user-attachments/assets/f66e01c1-3fbe-4d7e-a866-f71990c10247)

# since it was too dark, improving the normalization we get this:

![image](https://github.com/user-attachments/assets/c574e347-c50b-47a4-a460-961c9a27d7a1)

# now we'll add false color mapping, volume, a minimal N-body simulator with gravity and initial velocities based on dipole flow with large-scale anisotropies
![image](https://github.com/user-attachments/assets/d08db87a-4043-4378-a02d-1f52d2ba436b)

# After 100 steps, we get something like this:

![image](https://github.com/user-attachments/assets/9b55b45c-a3e5-4241-9a4b-21569dfac67e)

which is cool to watch but not ideal, the sphere is still hollow, the particles are not as granular as they should be and there is a fork on the road of decisions here:

1. Fill the sphere and make the particles more granular
2. Go for a holographic projection

I'll try both approaches, see which one yields the more promissing results, afterwards, I'm thinking of saving the dataset and moving to a CUDA simulation to support a more robust particle system, which should scale quite nicely

# filling the sphere based on the data on the surface from its surface resulted in this:
![image](https://github.com/user-attachments/assets/f711cbff-8e08-4b4b-aaec-ec4dcc124b4e)

Which is nice, but it most certainly makes me want to introduce smoothed oarticle hydrodynamics to it

After further attempts, Smoothed Particle Hydrodynamics seems to provide a more stable fluid dynamics solution

After adding ISPH it was needed to introduce Barnes–Hut Gravity since the complexity was too high

BHG's octree keeps subdividing indefinitely lead to a recurssion error
