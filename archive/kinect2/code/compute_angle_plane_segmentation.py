#!/usr/bin/env python


import numpy as np
import open3d as o3d

def segment_largest_plane(point_cloud, distance_threshold=0.01, ransac_n=3, num_iterations=1000):
    """
    Segment the largest plane in the point cloud using RANSAC.
    """
    plane_model, inliers = point_cloud.segment_plane(distance_threshold=distance_threshold,
                                                     ransac_n=ransac_n,
                                                     num_iterations=num_iterations)
    plane = point_cloud.select_by_index(inliers)
    return plane, plane_model

def calculate_angle_between_planes(plane_model1, plane_model2):
    """
    Calculate the angle between two planes given their plane models.
    Plane models are in the form of (a, b, c, d) where (a, b, c) is the normal vector.
    """
    normal1 = np.array(plane_model1[:3])
    normal2 = np.array(plane_model2[:3])
    
    # Normalize the normal vectors
    normal1 = normal1 / np.linalg.norm(normal1)
    normal2 = normal2 / np.linalg.norm(normal2)
    
    # Calculate the dot product and the angle
    dot_product = np.dot(normal1, normal2)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
    
    # Convert from radians to degrees
    angle_degrees = np.degrees(angle)
    
    return angle_degrees

def main():
    # Load the point clouds from .ply files
    pcd_d0 = o3d.io.read_point_cloud("../examples/experiment_greenbox_different_angles/point_cloud_frame_0.ply")
    pcd_d30 = o3d.io.read_point_cloud("../examples/experiment_greenbox_different_angles/point_cloud_frame_1.ply")
     
    # Visualize the original point clouds
    o3d.visualization.draw_geometries([pcd_d0, pcd_d30], window_name='Original Point Clouds')

    # Segment the largest planes
    plane_d0, plane_model_d0 = segment_largest_plane(pcd_d0)
    plane_d30, plane_model_d30 = segment_largest_plane(pcd_d30)

    # Calculate the angle between the largest planes
    angle = calculate_angle_between_planes(plane_model_d0, plane_model_d30)
    print(f"Angle between the largest planes: {angle:.2f} degrees")

    # Color the planes for visualization
    plane_d0.paint_uniform_color([1, 0, 0])  # Red
    plane_d30.paint_uniform_color([0, 0, 1])  # Blue
    print(pcd_d0)
    print(plane_d0)

    # Visualize the segmented planes
    o3d.visualization.draw_geometries([plane_d0, plane_d30])

if __name__ == "__main__":
    main()
