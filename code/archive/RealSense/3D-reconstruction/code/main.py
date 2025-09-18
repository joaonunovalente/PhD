#!/usr/bin/env python3
import copy
import numpy as np
import open3d as o3d
import time

from scipy.spatial.transform import Rotation as R


def draw_registration_result(source: o3d.geometry.PointCloud, 
                             target: o3d.geometry.PointCloud, 
                             transformation: np.ndarray):
    """
    Visualize the alignment of two point clouds (source and target) after applying 
    a transformation to the source point cloud. This function provides a simple way 
    to assess how well the two point clouds overlap after registration.

    Args:
        source (o3d.geometry.PointCloud): The source point cloud that will be transformed 
                                          and aligned to the target.
        target (o3d.geometry.PointCloud): The target point cloud that remains fixed and is 
                                          used as the reference for alignment.
        transformation (np.ndarray): A 4x4 transformation matrix that defines the rigid 
                                     transformation (rotation + translation) to be applied 
                                     to the source point cloud. This matrix should be of 
                                     shape (4, 4) and in homogeneous coordinates.

    Behavior:
        1. The source point cloud is transformed using the provided transformation matrix.
        2. Both point clouds are visualized in a 3D viewer.
           - The `source` point cloud is colored **yellow**.
           - The `target` point cloud is colored **cyan**.
        3. The function creates temporary copies of the original point clouds to avoid 
           modifying the originals.
        4. The degree of overlap between the source and target point clouds indicates 
           the quality of the registration.

    Example:
        >>> import open3d as o3d
        >>> import numpy as np
        >>> # Load example point clouds
        >>> source = o3d.io.read_point_cloud("source.pcd")
        >>> target = o3d.io.read_point_cloud("target.pcd")
        >>> # Define a transformation matrix
        >>> transformation = np.array([[0.862, 0.011, -0.507, 0.5],
                                       [-0.139, 0.967, -0.215, 0.7],
                                       [0.487, 0.255, 0.835, -1.4],
                                       [0.0, 0.0, 0.0, 1.0]])
        >>> # Visualize the registration result
        >>> draw_registration_result(source, target, transformation)

    Note:
        The transformation matrix should be in homogeneous coordinates, where the
        last row is `[0, 0, 0, 1]`. The first three rows define rotation and translation.
    """
    # Make deep copies of the source and target to avoid modifying the originals
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    
    # Set colors for the point clouds: yellow for the source and cyan for the target
    source_temp.paint_uniform_color([1, 0.706, 0])  # Yellow for source
    target_temp.paint_uniform_color([0, 0.651, 0.929])  # Cyan for target
    
    # Apply the transformation matrix to the source point cloud
    source_temp.transform(transformation)
    
    # Visualize the aligned point clouds
    o3d.visualization.draw_geometries([source_temp, target_temp],
                                      window_name='Point Clouds',
                                      width=800, height=600,
                                      left=50, top=50,
                                      point_show_normal=False,
                                      mesh_show_wireframe=False,
                                      mesh_show_back_face=False)
    

def load_point_clouds() -> tuple[o3d.geometry.PointCloud, o3d.geometry.PointCloud]:
    """
    Load the source and target meshes from specified file paths.

    Returns:
        tuple: A tuple containing the source and target point clouds.
    """
    if False:
        # Load the source and target meshes
        source_mesh = o3d.io.read_triangle_mesh("../data/front-view.ply")
        target_mesh = o3d.io.read_triangle_mesh("../data/side-view.ply")

        # Convert meshes to point clouds by sampling points uniformly from the mesh surface
        source_pcd = source_mesh.sample_points_uniformly(number_of_points=100_000)
        target_pcd = target_mesh.sample_points_uniformly(number_of_points=100_000)
    else:
        # Load the source and target point clouds
        source_pcd = o3d.io.read_point_cloud("../data/point_cloud_0001.ply")
        target_pcd = o3d.io.read_point_cloud("../data/point_cloud_0004.ply")
        # source_pcd = o3d.io.read_point_cloud("../data/golden_tree/point_cloud_0001.ply")
        # target_pcd = o3d.io.read_point_cloud("../data/golden_tree/point_cloud_0004.ply")

    return source_pcd, target_pcd


def preprocess_point_cloud(pcd: o3d.geometry.PointCloud, voxel_size: float) -> tuple[o3d.geometry.PointCloud, 
                                                                                     o3d.pipelines.registration.Feature]:
    """
    Downsample the point cloud and compute FPFH features for registration.

    Args:
        pcd (o3d.geometry.PointCloud): The input point cloud.
        voxel_size (float): The voxel size to use for downsampling.

    Returns:
        tuple: A tuple containing the downsampled point cloud and the computed FPFH features.
    """
    # Downsample the point cloud using the specified voxel size
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    # Estimate normals for the downsampled point cloud
    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    # Compute the Fast Point Feature Histogram (FPFH) for the downsampled point cloud
    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(pcd_down,
                                                               o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    
    return pcd_down, pcd_fpfh


def prepare_dataset(voxel_size: float) -> tuple[o3d.geometry.PointCloud, 
                                                o3d.geometry.PointCloud, 
                                                o3d.geometry.PointCloud, 
                                                o3d.geometry.PointCloud, 
                                                o3d.pipelines.registration.Feature, 
                                                o3d.pipelines.registration.Feature]:
    """
    Load and preprocess the source and target point clouds.

    Args:
        voxel_size (float): The voxel size to use for downsampling.

    Returns:
        tuple: A tuple containing the original source and target point clouds, 
               the downsampled source and target point clouds, and their corresponding FPFH features.
    """
    print(":: Load two point clouds and disturb initial pose.")
    # Load the source and target point clouds
    source, target = load_point_clouds()
    
    # Visualize the disturbed source and the target point clouds
    draw_registration_result(source, target, np.identity(4))

    # Preprocess both source and target point clouds (downsampling and FPFH feature extraction)
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    return source, target, source_down, target_down, source_fpfh, target_fpfh


def execute_global_registration(source_down: o3d.geometry.PointCloud, 
                                target_down: o3d.geometry.PointCloud, 
                                source_fpfh: o3d.pipelines.registration.Feature, 
                                target_fpfh: o3d.pipelines.registration.Feature, 
                                voxel_size: float) -> o3d.pipelines.registration.RegistrationResult:
    """
    Perform RANSAC-based global registration between two downsampled point clouds.

    Args:
        source_down (o3d.geometry.PointCloud): Downsampled source point cloud.
        target_down (o3d.geometry.PointCloud): Downsampled target point cloud.
        source_fpfh (o3d.pipelines.registration.Feature): FPFH feature of the source point cloud.
        target_fpfh (o3d.pipelines.registration.Feature): FPFH feature of the target point cloud.
        voxel_size (float): Voxel size used for downsampling.

    Returns:
        o3d.pipelines.registration.RegistrationResult: The registration result containing transformation matrix.
    """
    # Define the distance threshold for RANSAC based on voxel size
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    
    # Perform RANSAC-based feature matching for global registration
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True, distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False), 3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    
    return result


# def refine_registration(source: o3d.geometry.PointCloud, 
#                         target: o3d.geometry.PointCloud, 
#                         voxel_size: float, 
#                         result_ransac: o3d.pipelines.registration.RegistrationResult) -> o3d.pipelines.registration.RegistrationResult:
#     """
#     Refine the registration result using point-to-plane ICP (Iterative Closest Point).

#     Args:
#         source (o3d.geometry.PointCloud): Original source point cloud.
#         target (o3d.geometry.PointCloud): Original target point cloud.
#         voxel_size (float): Voxel size used for downsampling.
#         result_ransac (o3d.pipelines.registration.RegistrationResult): Initial transformation obtained from RANSAC.

#     Returns:
#         o3d.pipelines.registration.RegistrationResult: The refined registration result.
#     """
#     # Define a smaller distance threshold for ICP refinement
#     distance_threshold = voxel_size * 0.4
#     print(":: Point-to-plane ICP registration is applied on original point clouds")
#     print("   clouds to refine the alignment. This time we use a strict")
#     print("   distance threshold %.3f." % distance_threshold)
    
#     # Perform point-to-plane ICP to refine the alignment
#     result = o3d.pipelines.registration.registration_icp(source, 
#                                                          target, 
#                                                          distance_threshold, 
#                                                          result_ransac.transformation, 
#                                                          o3d.pipelines.registration.TransformationEstimationPointToPlane())
    
#     return result

def refine_registration(source: o3d.geometry.PointCloud, 
                        target: o3d.geometry.PointCloud, 
                        voxel_size: float, 
                        result_ransac: o3d.pipelines.registration.RegistrationResult) -> o3d.pipelines.registration.RegistrationResult:
    """
    Refine the registration result using point-to-plane ICP (Iterative Closest Point).

    Args:
        source (o3d.geometry.PointCloud): Original source point cloud.
        target (o3d.geometry.PointCloud): Original target point cloud.
        voxel_size (float): Voxel size used for downsampling.
        result_ransac (o3d.pipelines.registration.RegistrationResult): Initial transformation obtained from RANSAC.

    Returns:
        o3d.pipelines.registration.RegistrationResult: The refined registration result.
    """
    # Ensure normals are estimated for both source and target point clouds
    radius_normal = voxel_size * 2
    print(":: Estimate normals for the original point clouds.")
    
    source.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))
    target.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    # Define a smaller distance threshold for ICP refinement
    distance_threshold = voxel_size * 0.4
    print(":: Point-to-plane ICP registration is applied on original point clouds")
    print("   clouds to refine the alignment. This time we use a strict")
    print("   distance threshold %.3f." % distance_threshold)
    
    # Perform point-to-plane ICP to refine the alignment
    result = o3d.pipelines.registration.registration_icp(source, 
                                                         target, 
                                                         distance_threshold, 
                                                         result_ransac.transformation, 
                                                         o3d.pipelines.registration.TransformationEstimationPointToPlane())
    
    return result



def execute_fast_global_registration(source_down: o3d.geometry.PointCloud, 
                                     target_down: o3d.geometry.PointCloud, 
                                     source_fpfh: o3d.pipelines.registration.Feature, 
                                     target_fpfh: o3d.pipelines.registration.Feature, 
                                     voxel_size: float) -> o3d.pipelines.registration.RegistrationResult:
    """
    Perform Fast Global Registration (FGR) on two downsampled point clouds.

    Args:
        source_down (o3d.geometry.PointCloud): Downsampled source point cloud.
        target_down (o3d.geometry.PointCloud): Downsampled target point cloud.
        source_fpfh (o3d.pipelines.registration.Feature): FPFH feature of the source point cloud.
        target_fpfh (o3d.pipelines.registration.Feature): FPFH feature of the target point cloud.
        voxel_size (float): Voxel size used for downsampling.

    Returns:
        o3d.pipelines.registration.RegistrationResult: The registration result containing transformation matrix.
    """
    # Define the distance threshold for Fast Global Registration (FGR)
    distance_threshold = voxel_size * 0.5
    print(":: Apply fast global registration with distance threshold %.3f" % distance_threshold)
    
    # Perform Fast Global Registration (FGR) based on feature matching
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(maximum_correspondence_distance=distance_threshold))
    
    return result


def merge_point_clouds(source: o3d.geometry.PointCloud, target: o3d.geometry.PointCloud, transformation: np.ndarray) -> o3d.geometry.PointCloud:
    """
    Merge two point clouds by concatenating them into a single point cloud.

    Args:
        source (o3d.geometry.PointCloud): The source point cloud.
        target (o3d.geometry.PointCloud): The target point cloud.
        transformation (np.ndarray): The transformation matrix aligning the source to the target.

    Returns:
        o3d.geometry.PointCloud: The merged point cloud containing points from both input clouds.
    """
    # Make a deep copy of the source point cloud to avoid modifying the original
    source_temp = copy.deepcopy(source)

    # Apply the transformation to the source point cloud
    source_temp.transform(transformation)

    # Concatenate the source and target point clouds
    merged_cloud = source_temp + target
    
    return merged_cloud


def save_point_cloud(point_cloud: o3d.geometry.PointCloud, filename: str):
    """
    Save the point cloud to a file in PLY format.

    Args:
        point_cloud (o3d.geometry.PointCloud): The point cloud to save.
        filename (str): The name of the file to save the point cloud to.

    Returns:
        None
    """
    o3d.io.write_point_cloud(filename, point_cloud)
    print(f"Point cloud saved as {filename}")


def get_rotation_angle(transformation: np.ndarray) -> float:
    """
    Extracts the rotation angle from a 4x4 transformation matrix.
    
    Args:
        transformation (np.ndarray): A 4x4 transformation matrix.
    
    Returns:
        float: The rotation angle in degrees.
    """
    # Extract the 3x3 rotation matrix and make a writable copy
    rotation_matrix = np.array(transformation[:3, :3], copy=True)
    
    # Convert the rotation matrix to a rotation object
    rotation = R.from_matrix(rotation_matrix)
    
    # Get the rotation angle in degrees
    angle = np.rad2deg(rotation.magnitude())
    
    return angle


def main():
    """
    Main function to perform 3D point cloud registration between two views (source and target) 
    using different algorithms (RANSAC-based global registration, ICP, and Fast Global Registration).
    The process includes preprocessing the point clouds, applying feature matching, and refining 
    the alignment.

    Steps:
        1. Load and preprocess the source and target point clouds.
        2. Perform global registration using RANSAC.
        3. Refine the registration using Iterative Closest Point (ICP).
        4. Perform Fast Global Registration (FGR) for comparison.
        5. Merge the transformed source with the target point cloud
        6. Compute and display the rotation angle between the registered clouds.

    Note: 
        The dataset is downsampled to improve computational efficiency. Features are extracted
        using Fast Point Feature Histograms (FPFH), and various registration methods are compared 
        to find the best alignment.

    Returns:
        None
    """
    # ------------------------------------
    # Prepare the dataset and apply
    # FPFH (Fast Point Feature Histograms)
    # ------------------------------------
    
    # Set the voxel size for downsampling the point clouds.
    # Smaller voxel sizes yield higher point cloud resolution but increase computational cost.
    voxel_size = 0.05  # 1cm for this dataset

    # Load and preprocess the source and target point clouds.
    # The function `prepare_dataset` returns the original point clouds and their downsampled
    # versions along with FPFH features. This step involves:
    # - Downsampling the point clouds based on the defined voxel size.
    # - Estimating normals for the downsampled points.
    # - Computing the FPFH features for the downsampled clouds to facilitate feature matching.
    source, target, source_down, target_down, source_fpfh, target_fpfh = prepare_dataset(voxel_size)

    # Save the merged point cloud to a file (in PLY format)
    merged_cloud = merge_point_clouds(source, target, np.identity(4))
    save_point_cloud(merged_cloud, "../results/point_cloud_original.ply")

    # ------------------------------------
    # RANSAC-based Global Registration
    # ------------------------------------
    
    # Perform RANSAC-based global registration on the downsampled point clouds.
    # This method uses the FPFH features to find correspondences between the point clouds
    # and performs a RANSAC algorithm to find the best transformation.
    # It returns a transformation matrix aligning the source to the target.
    result_ransac = execute_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
    
    # Print the result of the RANSAC-based registration.
    print(result_ransac)

    # Visualize the result of RANSAC registration.
    # The transformed source point cloud will be displayed alongside the target to
    # check how well the two point clouds align.
    draw_registration_result(source_down, target_down, result_ransac.transformation)

    # Merge the transformed source with the target point cloud.
    merged_cloud = merge_point_clouds(source, target, result_ransac.transformation)
    save_point_cloud(merged_cloud, "../results/point_cloud_global_registration.ply")

    # ------------------------------------
    # Local refinement using ICP
    # ------------------------------------
    
    # Perform local refinement using Iterative Closest Point (ICP).
    # After global alignment from RANSAC, ICP is used to further refine the transformation 
    # by minimizing point-to-plane distances between the two point clouds.
    result_icp = refine_registration(source, target, voxel_size, result_ransac)
    
    # Print the result of ICP refinement.
    print(result_icp)
    
    # Visualize the refined registration after applying ICP.
    draw_registration_result(source, target, result_icp.transformation)

    # ------------------------------------
    # Fast Global Registration (FGR)
    # ------------------------------------

    if False:
        # Perform Fast Global Registration (FGR) as an alternative method for global alignment.
        # FGR is typically faster and uses feature matching like RANSAC but with different convergence criteria.
        start = time.time()  # Start time to measure the duration of FGR.

        # Apply FGR to the downsampled point clouds.
        result_fast = execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
        
        # Print the time taken for FGR to complete.
        print("Fast global registration took %.3f sec.\n" % (time.time() - start))
        
        # Print the result of Fast Global Registration.
        print(result_fast)
        
        # Visualize the result of FGR.
        draw_registration_result(source_down, target_down, result_fast.transformation)

    # ------------------------------------
    # Merge the transformed source with the target point cloud
    # ------------------------------------

    merged_cloud = merge_point_clouds(source, target, result_icp.transformation)
    save_point_cloud(merged_cloud, "../results/point_cloud_local_registration.ply")

    # ------------------------------------
    # Compute the rotation angle
    # ------------------------------------
    
    # Calculate the rotation angle in degrees from the transformation matrix obtained from FGR.
    # This gives an indication of how much the source point cloud was rotated during alignment.
    rotation_angle = get_rotation_angle(result_icp.transformation)
    
    # Print the computed rotation angle.
    print(f"Rotation angle: {rotation_angle:.2f} degrees")


if __name__ == "__main__":
    main()
