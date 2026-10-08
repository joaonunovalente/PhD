#!/usr/bin/env python3
import cv2
import os
import open3d as o3d
import numpy as np
from pyorbbecsdk import *
from typing import Union, Optional, Any

# Base directory to save point clouds
base_dir = os.path.join(os.getcwd(), "../data")

# Create the base directory if it doesn't exist
os.makedirs(base_dir, exist_ok=True)

# Count existing test directories
existing_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("test")]

# Determine the next test directory number
if existing_dirs:
    # Extract the numbers from the existing directory names and find the maximum
    existing_numbers = [int(d.replace("test", "")) for d in existing_dirs]
    next_number = max(existing_numbers) + 1
else:
    next_number = 1

# Create the new directory path for the next test
save_points_dir = os.path.join(base_dir, f"test{next_number}")

# Create the new directory
os.makedirs(save_points_dir, exist_ok=True)

ESC_KEY = 27

def frame_to_bgr_image(frame: VideoFrame) -> Union[Optional[np.array], Any]:
    width = frame.get_width()
    height = frame.get_height()
    color_format = frame.get_format()
    data = np.asanyarray(frame.get_data())
    image = np.zeros((height, width, 3), dtype=np.uint8)

    if color_format == OBFormat.RGB:
        image = np.resize(data, (height, width, 3))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    elif color_format == OBFormat.BGR:
        image = np.resize(data, (height, width, 3))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif color_format == OBFormat.YUYV:
        image = np.resize(data, (height, width, 2))
        image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_YUYV)
    elif color_format == OBFormat.MJPG:
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    elif color_format == OBFormat.I420:
        image = i420_to_bgr(data, width, height)
    elif color_format == OBFormat.NV12:
        image = nv12_to_bgr(data, width, height)
    elif color_format == OBFormat.NV21:
        image = nv21_to_bgr(data, width, height)
    elif color_format == OBFormat.UYVY:
        image = np.resize(data, (height, width, 2))
        image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_UYVY)
    else:
        print("Unsupported color format: {}".format(color_format))
        return None
    return image

def convert_to_o3d_point_cloud(points, colors=None):
    """
    Converts numpy arrays of points and colors (if provided) into an Open3D point cloud object.
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    if colors is not None:
        pcd.colors = o3d.utility.Vector3dVector(colors / 255.0)  # Assuming colors are in [0, 255]
    return pcd

def save_points_to_ply(frames: FrameSet, camera_param: OBCameraParam, saved_depth_cnt, voxel_size=20):
    """
    Saves the point cloud data to a PLY file using Open3D.
    """
    if frames is None:
        return 0
    depth_frame = frames.get_depth_frame()
    if depth_frame is None:
        return 0
    points = frames.get_point_cloud(camera_param)
    if points is None or len(points) == 0:
        print("No points to save.")
        return 0
    
    # Convert points to Open3D point cloud
    pcd = convert_to_o3d_point_cloud(np.array(points))
    
    # Downsampling using voxel grid filtering
    downsampled_pcd = pcd.voxel_down_sample(voxel_size)

    # Save to PLY file
    points_filename = os.path.join(save_points_dir, f"depth_{saved_depth_cnt}.ply")
    o3d.io.write_point_cloud(points_filename, downsampled_pcd)

    # Save the original point cloud without downsampling
    points_filename = os.path.join(save_points_dir, f"depth_{saved_depth_cnt}_original.ply")
    o3d.io.write_point_cloud(points_filename, pcd)
    
    return 1

def save_color_points_to_ply(frames: FrameSet, camera_param: OBCameraParam, saved_color_cnt, voxel_size=20):
    """
    Saves the color point cloud data to a PLY file using Open3D.
    """
    if frames is None:
        return 0
    depth_frame = frames.get_depth_frame()
    if depth_frame is None:
        return 0
    points = frames.get_color_point_cloud(camera_param)
    if points is None or points.shape[0] == 0:
        return 0
    
    # Assuming the color information is included in the points array
    # The points array contains xyz followed by color information (R, G, B)
    xyz = np.array(points[:, :3])
    colors = np.array(points[:, 3:], dtype=np.uint8)
    
    # Convert to Open3D point cloud with color
    pcd = convert_to_o3d_point_cloud(xyz, colors)

    # Downsampling using voxel grid filtering
    downsampled_pcd = pcd.voxel_down_sample(voxel_size)

    # Save to PLY file
    points_filename = os.path.join(save_points_dir, f"color_{saved_color_cnt}.ply")
    o3d.io.write_point_cloud(points_filename, downsampled_pcd)

    # Save the original point cloud without downsampling
    points_filename = os.path.join(save_points_dir, f"color_{saved_color_cnt}_original.ply")
    o3d.io.write_point_cloud(points_filename, pcd)

    return 1

def main():
    pipeline = Pipeline()
    device = pipeline.get_device()
    device_info = device.get_device_info()
    device_pid = device_info.get_pid()
    config = Config()
    has_color_sensor = False
    depth_profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
    
    if depth_profile_list is None:
        print("No proper depth profile, cannot generate point cloud")
        return
    depth_profile = depth_profile_list.get_default_video_stream_profile()
    config.enable_stream(depth_profile)
    
    try:
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if profile_list is not None:
            color_profile: VideoStreamProfile = profile_list.get_default_video_stream_profile()

            config.enable_stream(color_profile)
            if device_pid == 0x066B:
                # Femto Mega does not support hardware D2C, and it is changed to software D2C
                config.set_align_mode(OBAlignMode.SW_MODE)
            else:
                config.set_align_mode(OBAlignMode.HW_MODE)
            has_color_sensor = True
    except OBError as e:
        config.set_align_mode(OBAlignMode.DISABLE)
        print(f"Error setting up color sensor: {e}")

    pipeline.start(config)
    pipeline.enable_frame_sync()
    
    saved_color_cnt: int = 1
    saved_depth_cnt: int = 1
    voxel_size = 20  # Default voxel size, can be adjusted if needed
    
    while True:
        try:
            frames = pipeline.wait_for_frames(100)
            if frames is None:
                continue

            color_frame = frames.get_color_frame()
            if color_frame is None:
                continue

            # Convert color frame to OpenCV-compatible format (BGR)
            color_image = frame_to_bgr_image(color_frame)
            if color_image is None:
                print("Failed to convert frame to image.")
                continue

            # Display the color image
            cv2.imshow("Color Viewer", color_image)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):  # If 's' is pressed, save point cloud
                camera_param = pipeline.get_camera_param()
                saved_depth_cnt += save_points_to_ply(frames, camera_param, saved_depth_cnt, voxel_size)

                if has_color_sensor:
                    saved_color_cnt += save_color_points_to_ply(frames, camera_param, saved_color_cnt, voxel_size)

                print(f"Saved depth count: {saved_depth_cnt - 1}, Saved color count: {saved_color_cnt - 1}")

            elif key == ESC_KEY:  # If ESC is pressed, exit loop
                print("ESC pressed. Exiting...")
                break

        except OBError as e:
            print(f"Error during frame processing: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    cv2.destroyAllWindows()
    pipeline.stop()

if __name__ == "__main__":
    main()
