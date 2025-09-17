#!/usr/bin/env python3

import cv2 as cv
import numpy as np
from pylibfreenect2 import Freenect2, SyncMultiFrameListener, FrameType, Registration, Frame
import rospy

from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

def main():
    rospy.init_node('sender', anonymous=False)  # Initialize a ROS node named 'sender'
    topic = '/usb_cam/image_raw'  # Topic name for publishing images
    image_pub = rospy.Publisher(topic, Image, queue_size=10)
    bridge = CvBridge()

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

    try:
        while not rospy.is_shutdown():
            frames = listener.waitForNewFrame()

            color_frame = frames["color"]
            depth_frame = frames["depth"]

            # Register the depth image to the color image
            registration.apply(color_frame, depth_frame, undistorted, registered)

            # Convert the registered image to BGR format (from RGBA) and flip horizontally
            registered_rgba = registered.asarray(np.uint8)
            registered_bgr = cv.cvtColor(registered_rgba, cv.COLOR_RGBA2BGR)
            registered_bgr = cv.flip(registered_bgr, 1)

            # Convert the registered image to a ROS Image message
            try:
                image_message = bridge.cv2_to_imgmsg(registered_bgr, encoding="bgr8")
                image_message.header.stamp = rospy.Time.now()  # Add a timestamp to the message

                # Publish the ROS Image message
                image_pub.publish(image_message)
            except CvBridgeError as e:
                rospy.logerr(f"CvBridge Error: {e}")

            listener.release(frames)
    finally:
        # Clean up
        device.stop()
        device.close()
        cv.destroyAllWindows()

if __name__ == '__main__':
    main()
