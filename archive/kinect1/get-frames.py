#!/usr/bin/env python

import cv2
import os
import numpy as np

def extract_frames(video_path, output_folder, convert_to_grayscale=False):
    # Open the video file
    vidcap = cv2.VideoCapture(video_path)
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Read the video frames and save them as PNG files
    success, image = vidcap.read()
    count = 0
    while success:
        frame_path = os.path.join(output_folder, f"{count:06d}.png")

        if convert_to_grayscale:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = image.astype(np.uint16)
            image *= 2 ** 8


        # print(str(count) + str(new_image.shape))

        cv2.imwrite(frame_path, image)     # save frame as PNG

        success, image = vidcap.read()
        count += 1

# Example usage:
color_path = "data/videos/color.avi"
output_folder = "data/color"
extract_frames(color_path, output_folder)

# Example usage:
depth_path = "data/videos/depth.avi"
output_folder = "data/depth"
extract_frames(depth_path, output_folder, convert_to_grayscale=True)

