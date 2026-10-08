#!/usr/bin/env python3

import pickle
import numpy as np

def extract_transformation(matrix):
    translation = np.asarray(matrix[:3, 3])  # Ensure numpy array
    R = np.asarray(matrix[:3, :3])  # Convert rotation matrix to numpy array
    
    # Compute Euler angles (ZYX convention: yaw-pitch-roll)
    yaw = np.arctan2(R[1, 0], R[0, 0]).item()
    pitch = np.arcsin(-R[2, 0]).item()
    roll = np.arctan2(R[2, 1], R[2, 2]).item()
    
    # Convert to degrees
    yaw_deg = float(np.degrees(yaw))
    pitch_deg = float(np.degrees(pitch))
    roll_deg = float(np.degrees(roll))
    
    return translation.tolist(), (roll_deg, pitch_deg, yaw_deg)

def load_transformations(pickle_path):
    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)
    
    est_matrix = np.asarray(data.get("estimated-transformation"))
    ref_matrix = np.asarray(data.get("refined-transformation"))
    
    est_translation, est_angles = extract_transformation(est_matrix)
    ref_translation, ref_angles = extract_transformation(ref_matrix)
    
    return est_matrix, est_translation, est_angles, ref_matrix, ref_translation, ref_angles

if __name__ == "__main__":
    pickle_path = '../data/transformation_matrix/results_and_parameters.pickle'
    est_matrix, est_translation, est_angles, ref_matrix, ref_translation, ref_angles = load_transformations(pickle_path)
    
    print("--------- Estimated Transformation -----------")
    print("Translation:", est_translation)
    print("Rotation (Roll, Pitch, Yaw):", est_angles)
    print("\n")
    
    print("--------- Refined Transformation -----------")
    print("Translation:", ref_translation)
    print("Rotation (Roll, Pitch, Yaw):", ref_angles)