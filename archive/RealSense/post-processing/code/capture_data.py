#!/usr/bin/env python

import pyrealsense2 as rs
import numpy as np
import cv2
import os

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

# Directory to save images
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

        # Convert images to numpy arrays for OpenCV
        depth_image = np.asanyarray(depth_frame.get_data())
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

            # Increment the image counter
            image_counter += 1

        elif key == 27 or key == ord('q'):
            # Exit the loop when 'Esc' or 'q' is pressed
            break

finally:
    # Stop streaming and close windows
    pipeline.stop()
    cv2.destroyAllWindows()
