#!/usr/bin/env python3

# Import necessary libraries
import cv2
import numpy as np
import pyrealsense2 as rs
import rospy

from cv_bridge import CvBridge
from sensor_msgs.msg import Image

# Initialize ROS topic and publisher
topic = '/usb_cam/image_raw'  # Topic name for publishing images
image_pub = rospy.Publisher(topic, Image, queue_size=10)
bridge = CvBridge()

# Configure the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()

# Enable depth and color streams with specific resolutions and frame rates
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)  # Depth stream
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)  # Color stream

# Start the RealSense pipeline with the configuration
pipeline.start(config)
rospy.init_node('sender', anonymous=False)  # Initialize a ROS node named 'sender'

try:
    while not rospy.is_shutdown():  # Loop until ROS is shutdown
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()  # Get frames from the camera

        # Get the color frame
        color_frame = frames.get_color_frame()
        
        if not color_frame:  # If no color frame is received, continue to the next iteration
            continue

        # Convert the color frame to a numpy array
        color_image = np.asanyarray(color_frame.get_data())

        # Convert the color image to a grayscale image using OpenCV
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # Convert the grayscale image to a ROS Image message
        image_message = bridge.cv2_to_imgmsg(color_image, encoding="mono8")
        image_message.header.stamp = rospy.Time.now()  # Add a timestamp to the message

        # Publish the ROS Image message
        image_pub.publish(image_message)

finally:
    # Stop the RealSense pipeline when done
    pipeline.stop()
