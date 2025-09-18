#!/usr/bin/env python3
import os
import cv2
import numpy as np
from pyorbbecsdk import *

# Base directory to save point clouds
base_dir = os.path.join(os.getcwd(), "../data")
os.makedirs(base_dir, exist_ok=True)

# Count existing test directories
existing_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("test")]
next_number = max([int(d.replace("test", "")) for d in existing_dirs], default=0) + 1
save_points_dir = os.path.join(base_dir, f"test{next_number}")
os.makedirs(save_points_dir, exist_ok=True)

ESC_KEY = 27

def frame_to_bgr_image(frame: VideoFrame):
    """Convert Orbbec VideoFrame to OpenCV BGR image."""
    if frame is None:
        return None
    fmt = frame.get_format()
    data = np.asarray(frame.get_data())
    h, w = frame.get_height(), frame.get_width()

    if fmt == OBFormat.RGB:
        img = data.reshape(h, w, 3)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif fmt == OBFormat.BGR:
        img = data.reshape(h, w, 3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif fmt == OBFormat.MJPG:
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    else:
        print(f"Unsupported format: {fmt}")
        return None
    return img

def main():
    pipeline = Pipeline()
    config = Config()

    # Enable depth stream
    depth_profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
    if depth_profile_list is None:
        print("No depth stream available.")
        return
    depth_profile = depth_profile_list.get_default_video_stream_profile()
    config.enable_stream(depth_profile)

    # Enable color stream if available
    has_color = False
    try:
        color_profiles = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if color_profiles:
            color_profile = color_profiles.get_default_video_stream_profile()
            config.enable_stream(color_profile)
            has_color = True
    except OBError as e:
        print(f"Color sensor unavailable: {e}")

    pipeline.enable_frame_sync()
    pipeline.start(config)

    align_filter = AlignFilter(align_to_stream=OBStreamType.COLOR_STREAM if has_color else OBStreamType.DEPTH_STREAM)
    point_filter = PointCloudFilter()

    saved_depth_cnt = 1
    saved_color_cnt = 1
    point_filter.set_create_point_format(OBFormat.POINT)  # default depth
    if has_color:
        point_filter_color = PointCloudFilter()
        point_filter_color.set_create_point_format(OBFormat.RGB_POINT)

    while True:
        frames = pipeline.wait_for_frames(100)
        if frames is None:
            continue

        color_frame = frames.get_color_frame() if has_color else None
        if has_color and color_frame is None:
            continue

        # Display color image
        color_img = frame_to_bgr_image(color_frame) if has_color else None
        if color_img is not None:
            cv2.imshow("Color Viewer", color_img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):  # Save point clouds
            aligned = align_filter.process(frames)

            # Save depth point cloud
            point_filter.set_create_point_format(OBFormat.POINT)
            pc_depth = point_filter.process(aligned)
            if pc_depth:
                depth_filename = os.path.join(save_points_dir, f"depth_{saved_depth_cnt}.ply")
                save_point_cloud_to_ply(depth_filename, pc_depth)
                print(f"Saved depth point cloud: {depth_filename}")
                saved_depth_cnt += 1

            # Save color point cloud
            if has_color:
                pc_color = point_filter_color.process(aligned)
                if pc_color:
                    color_filename = os.path.join(save_points_dir, f"color_{saved_color_cnt}.ply")
                    save_point_cloud_to_ply(color_filename, pc_color)
                    print(f"Saved color point cloud: {color_filename}")
                    saved_color_cnt += 1

        elif key == ESC_KEY:
            print("ESC pressed. Exiting...")
            break

    cv2.destroyAllWindows()
    pipeline.stop()

if __name__ == "__main__":
    main()
