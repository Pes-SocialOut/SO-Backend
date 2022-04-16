import os
# switch to "osmesa" or "egl" before loading pyrender
os.environ["PYOPENGL_PLATFORM"] = "osmesa"

import numpy as np
import pyrender
import trimesh
import matplotlib.pyplot as plt

# generate mesh
sphere = trimesh.creation.icosphere(subdivisions=4, radius=0.8)
sphere.vertices+=1e-2*np.random.randn(*sphere.vertices.shape)
mesh = pyrender.Mesh.from_trimesh(sphere, smooth=False)

# compose scene
scene = pyrender.Scene(ambient_light=[.1, .1, .3], bg_color=[0, 0, 0])
camera = pyrender.PerspectiveCamera( yfov=np.pi / 3.0)
light = pyrender.DirectionalLight(color=[1,1,1], intensity=2e3)

scene.add(mesh, pose=  np.eye(4))
scene.add(light, pose=  np.eye(4))

c = 2**-0.5
scene.add(camera, pose=[[ 1,  0,  0,  0],
                        [ 0,  c, -c, -2],
                        [ 0,  c,  c,  2],
                        [ 0,  0,  0,  1]])

# render scene
r = pyrender.OffscreenRenderer(512, 512)
color, _ = r.render(scene)

plt.figure(figsize=(8,8))
plt.imshow(color)