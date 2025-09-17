#!/usr/bin/env python

import open3d as o3d
import numpy as np

# Load point cloud
point_cloud_path = "../data/point_cloud_0001.ply"
point_cloud = o3d.io.read_point_cloud(point_cloud_path)

# Load the mesh
ply_file_path = "../data/domino-box.ply"
mesh = o3d.io.read_triangle_mesh(ply_file_path)
mesh = mesh.sample_points_uniformly(number_of_points=100000)

# Get the centroids of the point cloud and mesh
pcd_center = point_cloud.get_center()
mesh_center = mesh.get_center()

# Translate both to the origin
point_cloud.translate(-pcd_center)
mesh.translate(-mesh_center)

# Optionally apply the scaling if you haven't done it yet
pcd_bbox = point_cloud.get_axis_aligned_bounding_box()
mesh_bbox = mesh.get_axis_aligned_bounding_box()
scale_factor = np.max(pcd_bbox.get_extent()) / np.max(mesh_bbox.get_extent())
scale_factor = 0.001
mesh.scale(scale_factor, center=(0, 0, 0))

# Visualize the centered objects
o3d.visualization.draw_geometries([point_cloud, mesh], window_name="Centered 3D Visualization")
