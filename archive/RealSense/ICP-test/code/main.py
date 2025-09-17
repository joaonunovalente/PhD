#!/usr/bin/env python3
import open3d as o3d
import numpy as np
import os


def load_meshes(source_mesh_path, target_mesh_path):
    """
    Load the source and target meshes from the specified file paths.

    Parameters:
    - source_mesh_path (str): The file path for the source mesh.
    - target_mesh_path (str): The file path for the target mesh.

    Returns:
    - source_mesh (o3d.geometry.TriangleMesh): The loaded source mesh.
    - target_mesh (o3d.geometry.TriangleMesh): The loaded target mesh.
    """
    source_mesh = o3d.io.read_triangle_mesh(source_mesh_path)
    target_mesh = o3d.io.read_triangle_mesh(target_mesh_path)

    return source_mesh, target_mesh


def convert_to_point_clouds(source_mesh, target_mesh):
    """
    Convert the source and target meshes to point clouds and paint them with different colors.

    Parameters:
    - source_mesh (o3d.geometry.TriangleMesh): The source mesh to convert.
    - target_mesh (o3d.geometry.TriangleMesh): The target mesh to convert.

    Returns:
    - source (o3d.geometry.PointCloud): The converted and colored source point cloud.
    - target (o3d.geometry.PointCloud): The converted and colored target point cloud.
    """
    source = source_mesh.sample_points_uniformly(number_of_points=10_000)
    target = target_mesh.sample_points_uniformly(number_of_points=100_000)
    
    # Paint the point clouds
    source.paint_uniform_color([1, 0.984, 0])  # Yellow color for source
    target.paint_uniform_color([0, 0.784, 1])  # Light blue color for target
    
    return source, target


def rotate_and_translate_point_cloud(source, angle_degrees, translation):
    """
    Rotate and translate the source point cloud.

    Parameters:
    - source (o3d.geometry.PointCloud): The source point cloud to be transformed.
    - angle_degrees (float): The rotation angle in degrees for rotation around the z-axis.
    - translation (tuple): The translation vector (x, y, z) to apply to the point cloud.

    Returns:
    - source (o3d.geometry.PointCloud): The transformed source point cloud.
    """
    # Define the rotation angle in degrees and convert to radians
    angle_radians = np.deg2rad(angle_degrees)
    
    # Create a rotation matrix for a rotation around the z-axis
    R = source.get_rotation_matrix_from_axis_angle([0, 0, angle_radians])
    
    # Rotate and translate the source point cloud
    source.rotate(R, center=(0, 0, 0))
    source.translate(translation)
    
    return source


def save_point_cloud(point_cloud, file_path):
    """
    Save a point cloud to the specified file path.

    Parameters:
    - point_cloud (o3d.geometry.PointCloud): The point cloud to save.
    - file_path (str): The file path where the point cloud will be saved.
    """
    o3d.io.write_point_cloud(file_path, point_cloud)
    print(f"Point cloud saved to {file_path}")


def save_merged_point_cloud(source, target, file_path):
    """
    Merge two point clouds and save the merged result.

    Parameters:
    - source (o3d.geometry.PointCloud): The source point cloud.
    - target (o3d.geometry.PointCloud): The target point cloud.
    - file_path (str): The file path where the merged point cloud will be saved.
    """
    merged_point_cloud = source + target
    save_point_cloud(merged_point_cloud, file_path)


def apply_icp(source, target, threshold):
    """
    Apply the ICP algorithm to align the source point cloud with the target.

    Parameters:
    - source (o3d.geometry.PointCloud): The source point cloud.
    - target (o3d.geometry.PointCloud): The target point cloud.
    - threshold (float): The distance threshold for ICP.

    Returns:
    - transformation_matrix (np.ndarray): The resulting transformation matrix from ICP.
    """
    trans_init = np.eye(4)  # Initial transformation matrix (identity matrix)
    reg_p2p = o3d.pipelines.registration.registration_icp(
        source, target, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint()
    )
    source.transform(reg_p2p.transformation)
    return reg_p2p.transformation


def main():
    """
    Main function that aligns two meshes, transforms them into point clouds, 
    applies ICP, and saves the merged point clouds.

    - Loads source and target meshes.
    - Converts them to point clouds.
    - Applies rotation and translation to the source point cloud.
    - Merges and saves the initial, transformed, and ICP aligned point clouds.
    """
    # File paths and parameters
    source_mesh_path = "../data/domino-plane.ply"
    target_mesh_path = "../data/domino-box.ply"
    results_dir = "../results"
    angle_degrees = 45
    translation = (-10, 100, 20)
    threshold = 200

    # Ensure the output directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Load source and target meshes
    source_mesh, target_mesh = load_meshes(source_mesh_path, target_mesh_path)

    # Convert both meshes to point clouds
    original_source, target = convert_to_point_clouds(source_mesh, target_mesh)

    # Visualize the original point clouds and save the merged original point clouds
    o3d.visualization.draw_geometries([original_source, target], window_name="Original Point Clouds")
    save_merged_point_cloud(original_source, target, os.path.join(results_dir, "1. original_point_cloud.ply"))

    # Rotate and translate the source point cloud
    transformed_source = rotate_and_translate_point_cloud(original_source, angle_degrees, translation)

    # Visualize the transformed point cloud and save the merged transformed point clouds
    o3d.visualization.draw_geometries([transformed_source, target], window_name="Transformed Point Clouds")
    save_merged_point_cloud(transformed_source, target, os.path.join(results_dir, "2. transformed_point_cloud.ply"))

    # Apply ICP and visualize/save the merged ICP-aligned point clouds
    transformation_matrix = apply_icp(transformed_source, target, threshold)
    o3d.visualization.draw_geometries([transformed_source, target], window_name="ICP Aligned Point Clouds")
    save_merged_point_cloud(transformed_source, target, os.path.join(results_dir, "3. icp_point_cloud.ply"))

    # Print the transformation matrix from ICP
    print("Transformation Matrix:")
    print(transformation_matrix)


if __name__ == "__main__":
    main()
