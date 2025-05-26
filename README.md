
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

# interesting results, it collapsed into a cube
![image](https://github.com/user-attachments/assets/c326aee4-72d9-4ac4-95db-7d6a83201513)

which is interesting as the cctree biases symmetrically, the spatial subdivision introduces grid-aligned biases, especially when many nodes have near-equal mass and distance: Leading to a shape that resembles the cube bounding box.

ok, I think its time to investigate the holographic hypothesis now, filling the sphere and adding ISPH resulted in having to change the algorithm running the gravity to avoid big-o time-space complexity, which introduced biases and wasn't all that worth it. Onwards towards the second option to keep moving forward.

The first attempt at the holographic script resulted in a humorous way:
- All HEALPix pixels at nside=2048 → ≈ 50 million points on the sphere
- Then multiplying that by n_depth = 10 → 500+ million 3D points
- Then trying to store and visualize all of them at once

Which is interesting, it is something that a CUDA script could most certainly handle

# CMD shell with holographic memory safe solution resulted in this:

![image](https://github.com/user-attachments/assets/3ff55196-fd0f-4849-91a2-5781d182a29e)

and here is a 480p quick video on it, quality was compressed do to github's limitation, so its 2.75x sped up to fit the 10mb file limtation:

https://github.com/user-attachments/assets/ac0e64ee-730b-4811-b6c5-47ac02ba70f4

# Now, I'll add a colormap (like plasma) to assign visually rich RGB values based on CMB intensity, which resulted in:

https://github.com/user-attachments/assets/12dd7566-3329-4a77-b04d-c94c58bab117

now, we can use the dust-heavy 857Ghz, the 545Ghz synchroton and 143Ghz CMB to create a multi frequency CMD shell holographic visualization, which resulted in:

https://github.com/user-attachments/assets/f7552c91-c76e-41bc-b9ca-acfe83c50c0b

So, the next logical step, considering the downsampling was to go over the math and with at least 6gb you can run the full map.

This is what gave rise to the dataset creation python3 script. The first attempt to run on cuda with no downsampling resulted in this:

![image](https://github.com/user-attachments/assets/460b7a77-a8c9-4e61-b045-ebba6af7779e)

Which is interesting, but I probably got something wrong, so I'll investigate it further 

And, after exploring a bit, this was found:

![image](https://github.com/user-attachments/assets/73d4fe07-4596-4341-932b-dda559181336)
