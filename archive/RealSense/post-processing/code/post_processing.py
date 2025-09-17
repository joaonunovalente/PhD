#!/usr/bin/env python

import pyrealsense2 as rs
import numpy as np
import cv2
import open3d as o3d
import os

# Function to load camera intrinsics from your calibration data
def get_intrinsics_from_calibration():
    intrinsics = {
        'width': 640,
        'height': 480,
        'fx': 640.0,  # Focal length X (example value, adjust as necessary)
        'fy': 640.0,  # Focal length Y (example value, adjust as necessary)
        'cx': 320.0,  # Principal point X
        'cy': 240.0,  # Principal point Y
        'depth_scale': 0.001  # Depth scale, adjust if necessary
    }
    return intrinsics

# Function to create a point cloud from RGB and depth images
def create_point_cloud(color_image, depth_image, output_file='point_cloud.ply'):
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

# Initialize the Intel RealSense pipeline
pipeline = rs.pipeline()

# Create a config object to configure the pipeline
config = rs.config()

# Enable the depth and color streams with desired resolutions and frame rates
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Create an align object to align depth frames to color frames
align_to = rs.stream.color
align = rs.align(align_to)

# Create filters
spatial_filter = rs.spatial_filter()
temporal_filter = rs.temporal_filter()
hole_filling_filter = rs.hole_filling_filter()

# Directory to save images and point cloud
save_dir = "../data/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Image counter for numbering
image_counter = 1

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get the aligned frames
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not depth_frame or not color_frame:
            continue

        # Apply filters to the depth frame
        depth_frame_filtered = spatial_filter.process(depth_frame)
        depth_frame_filtered = temporal_filter.process(depth_frame_filtered)
        depth_frame_filtered = hole_filling_filter.process(depth_frame_filtered)

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame_filtered.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply a colormap to the depth image for better visualization
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
        )

        # Stack the color and depth images horizontally
        images = np.hstack((color_image, depth_colormap))

        # Display the combined image
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)

        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            # Format the filenames with leading zeros for sequential numbering
            color_filename = os.path.join(save_dir, f"color_{image_counter:04d}.png")
            depth_filename = os.path.join(save_dir, f"depth_{image_counter:04d}.png")

            # Save the color and depth images
            cv2.imwrite(color_filename, color_image)
            cv2.imwrite(depth_filename, depth_image)

            print(f"Images saved: {color_filename} and {depth_filename}")

            # Create and save the point cloud
            point_cloud_file = os.path.join(save_dir, f"point_cloud_{image_counter:04d}.ply")
            create_point_cloud(color_image, depth_image, point_cloud_file)

            # Increment the image counter
            image_counter += 1

        elif key == 27 or key == ord('q'):
            # Exit the loop when 'Esc' or 'q' is pressed
            break

finally:
    # Stop streaming and close windows
    pipeline.stop()
    cv2.destroyAllWindows()
