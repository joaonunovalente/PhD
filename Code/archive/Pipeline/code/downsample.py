#!/usr/bin/env python3

import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

# Provide the path to your point cloud file
input_path = "../data/test1/depth_1.ply"  # Change this to your actual file path
output_path = "../data/test1/depth_1_downsampled.ply"

# Load the point cloud
pcd = o3d.io.read_point_cloud(input_path)

# Downsampling using voxel grid
voxel_size = 20 # Adjust this value for different downsampling levels
downsampled_pcd = pcd.voxel_down_sample(voxel_size)

# Save the downsampled point cloud
o3d.io.write_point_cloud(output_path, downsampled_pcd)
print(f"Downsampled point cloud saved to {output_path}")


# Show the point cloud in Open3D
o3d.visualization.draw_geometries([downsampled_pcd], window_name="Downsampled Point Cloud")

if __name__ == "__main__":
    pass
