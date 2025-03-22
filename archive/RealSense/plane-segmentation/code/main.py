#!/usr/bin/env python

# PhD
# Joao Nuno Valente, DEM, UA

import pyrealsense2 as rs
import numpy as np
import cv2 as cv
import os

def main():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Enable depth and color streams
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    # Create directories if they don't exist
    color_dir = "../data/color"
    depth_dir = "../data/depth"

    os.makedirs(color_dir, exist_ok=True)
    os.makedirs(depth_dir, exist_ok=True)

    frame_count = 0

    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()

        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        
        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Save the color and depth image
        depth_image_path = os.path.join(depth_dir, f'{frame_count:04d}.png')
        color_image_path = os.path.join(color_dir, f'{frame_count:04d}.png')

        cv.imwrite(depth_image_path, depth_image)  
        cv.imwrite(color_image_path, color_image)

        # Show images
        cv.imshow('Color Video', color_image)
        cv.imshow('Depth Video', depth_image)

        frame_count += 1

        if cv.waitKey(1) == 27:  # Exit on ESC key
            break

    # Stop streaming and close OpenCV windows
    pipeline.stop()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
