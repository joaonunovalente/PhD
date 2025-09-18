#!/usr/bin/env python

import os
import freenect
import cv2 as cv
import numpy as np

# Define the directory paths
example_dir = "data/example10"
videos_dir = os.path.join(example_dir, "videos")
color_dir = os.path.join(example_dir, "color")
depth_dir = os.path.join(example_dir, "depth")

# Create the directories if they don't exist
os.makedirs(videos_dir, exist_ok=True)
os.makedirs(color_dir, exist_ok=True)
os.makedirs(depth_dir, exist_ok=True)

def get_depth():
    array, _ = freenect.sync_get_depth()
    return array.astype(np.uint16)

def get_video():
    array, _ = freenect.sync_get_video()
    return array.astype(np.uint8)

# Define the codec and create VideoWriter object
color_fourcc = cv.VideoWriter_fourcc(*'XVID')
color_out = cv.VideoWriter(videos_dir + '/color.avi', color_fourcc, 30.0, (630, 480))

# Define the codec for depth frames and create VideoWriter object
depth_fourcc = cv.VideoWriter_fourcc(*'XVID')
depth_out = cv.VideoWriter(videos_dir + '/depth.avi', depth_fourcc, 30.0, (630, 480), isColor = False)

count = 0  # Initialize frame count

while True:
    depth_frame = get_depth()
    color_frame = get_video() 

    # # Remove right side bar
    depth_frame = depth_frame[:,:630]
    color_frame = color_frame[:,:630]
    
    # Define frame name '0001.png', '0002.png', ...
    depth_frame_path = os.path.join(depth_dir, f"{count:04d}.png")
    color_frame_path = os.path.join(color_dir, f"{count:04d}.png")
    
    # Save frame as an image file
    cv.imwrite(color_frame_path, color_frame)
    cv.imwrite(depth_frame_path, depth_frame)

    # Convert depth frames from uint16 to uint8
    # depth_frame = depth_frame.astype(np.uint16) * 2 ** 8
    # depth_frame = depth_frame * 2 ** 5

    depth_frame = depth_frame * 2 ** 5

    # Display frames
    cv.imshow('Color', color_frame)
    cv.imshow('Depth', depth_frame)

    depth_frame = depth_frame / 2 ** 8

    depth_frame = depth_frame.astype(np.uint8)

    # Write frames to video files
    color_out.write(color_frame)     
    depth_out.write(depth_frame)
    
    count += 1  # Increment frame count

    # Break the loop if 'Esc' key is pressed
    if cv.waitKey(10) == 27:
        break

# Release VideoWriters and close OpenCV windows
color_out.release()
depth_out.release()
cv.destroyAllWindows()



