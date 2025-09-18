#!/usr/bin/env python

import cv2
import numpy as np
import open3d as o3d


def depth_to_point_cloud(depth_img, rgb_img, fx, fy, cx, cy):
    rows, cols = depth_img.shape
    points = []

    for y in range(rows):
        for x in range(cols):
            Z = depth_img[y, x]
            if Z == 0:  # Skip points with zero depth
                continue
            X = (x - cx) * Z / fx
            Y = (y - cy) * Z / fy
            color = rgb_img[y, x]
            points.append([X, Y, Z, *color])

    return np.array(points)

def main():
    filename = 'data/example8/'
    frame = '0300'
    # Load depth image and RGB image
    depth_img = cv2.imread(filename + 'depth/' + frame + '.png', cv2.IMREAD_ANYDEPTH)
    rgb_img = cv2.imread(filename + 'color/' + frame + '.png')

    # Intrinsic parameters (fx, fy, cx, cy)
    fx, fy, cx, cy = 1500, 1500, 320, 240

    # Convert depth image to point cloud
    points = depth_to_point_cloud(depth_img, rgb_img, fx, fy, cx, cy)

    # Create PointCloud object
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points[:, :3])
    pcd.colors = o3d.utility.Vector3dVector(points[:, 3:] / 255.0)  # Normalize RGB values

    # Save point cloud as .ply file
    o3d.io.write_point_cloud(filename + frame + '-1500.ply', pcd)

if __name__ == "__main__":
    main()
