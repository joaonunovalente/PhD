#!/usr/bin/env python3


import cv2 as cv
import numpy as np
from pylibfreenect2 import Freenect2, SyncMultiFrameListener, FrameType, Registration, Frame

# Initialize the Freenect2 device
fn = Freenect2()
if fn.enumerateDevices() == 0:
    print("No device connected!")
    exit(1)

# Open the first device
serial = fn.getDeviceSerialNumber(0)
device = fn.openDevice(serial)

# Create a listener
listener = SyncMultiFrameListener(FrameType.Color | FrameType.Ir | FrameType.Depth)

# Register the listener to the device
device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

# Start the device
device.start()

# Create registration object with custom parameters
registration = Registration(device.getIrCameraParams(), device.getColorCameraParams())

# Arrays for storing frames
undistorted = Frame(512, 424, 4)
registered = Frame(512, 424, 4)

frame_count = 0  # Initialize frame counter

while True:
    frames = listener.waitForNewFrame()

    color_frame = frames["color"]
    depth_frame = frames["depth"]

    # Convert the color image to BGR format and flip horizontally
    color = cv.flip(color_frame.asarray(np.uint8), 1)

    # Flip the depth image horizontally
    depth = cv.flip(depth_frame.asarray(np.float32), 1)

    # Apply registration
    registration.apply(color_frame, depth_frame, undistorted, registered)

    # Normalize depth for display
    depth_display = cv.normalize(depth, None, 0, 1, cv.NORM_MINMAX, cv.CV_32F)

    # Convert registered image to BGR format and flip horizontally
    registered_image = cv.flip(registered.asarray(np.uint8), 1)

    # Display the images
    cv.imshow('Color', color)
    cv.imshow('Depth', depth_display)
    cv.imshow('Registered Image', registered_image)

    key = cv.waitKey(1) & 0xFF
    if key == 27:  # Press 'ESC' to exit
        break
    elif key == ord('s'):  # Press 's' to save frames
        cv.imwrite(f'../data/registered_image_{frame_count}.png', registered_image)
        cv.imwrite(f'../data/color_frame_{frame_count}.png', color)
        cv.imwrite(f'../data/depth_frame_{frame_count}.png', depth_display * 255)  # Normalize depth for saving as image
        frame_count += 1
        print(f"Saved color_frame_{frame_count}.png and depth_frame_{frame_count}.png")

    listener.release(frames)

# Clean up
device.stop()
device.close()
cv.destroyAllWindows()
