#!/usr/bin/env python

import os
import numpy as np
import cv2
import open3d as o3d

# Function to load camera intrinsics from your calibration data
def get_intrinsics_from_calibration():
    intrinsics = {
        'width': 640,
        'height': 480,
        'fx': 617.797551,  # Focal length X
        'fy': 620.040790,  # Focal length Y
        'cx': 317.384525,  # Principal point X
        'cy': 256.749749,  # Principal point Y
        'depth_scale':  0.001 # Depth scale, adjust if necessary
    }
    return intrinsics

# Function to create a point cloud from RGB and depth images
def create_point_cloud(color_image_file, depth_image_file, output_file='point_cloud.ply'):
    # Load color and depth images
    color_image = cv2.imread(color_image_file)
    depth_image = cv2.imread(depth_image_file, cv2.IMREAD_UNCHANGED)  # Load as 16-bit depth image
    
    if color_image is None or depth_image is None:
        print(f"Error: Could not load images. Check paths:\n{color_image_file}\n{depth_image_file}")
        return

    # Get camera intrinsics from calibration
    intrinsics = get_intrinsics_from_calibration()

    fx = intrinsics['fx']
    fy = intrinsics['fy']
    cx = intrinsics['cx']
    cy = intrinsics['cy']
    depth_scale = intrinsics['depth_scale']

    height, width = depth_image.shape

    # Create empty lists for points and colors
    points = []
    colors = []

    for y in range(height):
        for x in range(width):
            # Get depth value at (x, y) in meters
            depth_value = depth_image[y, x] * depth_scale
            if depth_value > 0:
                # Calculate 3D coordinates using the pinhole camera model
                z = depth_value
                x_3d = (x - cx) * z / fx
                y_3d = (y - cy) * z / fy

                # Get the color at this pixel
                color = color_image[y, x]
                r, g, b = color[2] / 255.0, color[1] / 255.0, color[0] / 255.0

                # Append the 3D point and its color
                points.append([x_3d, y_3d, z])
                colors.append([r, g, b])

    # Convert lists to numpy arrays
    points = np.array(points)
    colors = np.array(colors)

    # Create the Open3D point cloud object
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)
    point_cloud.colors = o3d.utility.Vector3dVector(colors)

    # Save the point cloud as a .ply file
    o3d.io.write_point_cloud(output_file, point_cloud)
    print(f"Point cloud saved as '{output_file}'.")

# Main code to run the point cloud creation
if __name__ == "__main__":
    # Directory where images are saved
    save_dir = "../data/"  # Update with the correct directory path
    image_counter = 1  # Set the image counter to the desired number

    # Construct filenames based on image_counter
    color_filename = os.path.join(save_dir, f"color_{image_counter:04d}.png")
    depth_filename = os.path.join(save_dir, f"depth_{image_counter:04d}.png")

    # Output point cloud filename
    output_file = save_dir + f"point_cloud_{image_counter:04d}.ply"

    # Create the point cloud
    create_point_cloud(color_filename, depth_filename, output_file)
