#!/usr/bin/env python


import open3d as o3d

# Load the point cloud
file_path = "../examples/experiment_greenbox_different_angles/point_cloud_frame_3.ply"
pcd = o3d.io.read_point_cloud(file_path)
print(pcd)

# Downsample point cloud
pcd = pcd.voxel_down_sample(voxel_size=0.005)
print(pcd)

# Visualize the point cloud
o3d.visualization.draw_geometries([pcd])
