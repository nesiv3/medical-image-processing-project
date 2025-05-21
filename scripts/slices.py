import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

def extract_final_slice(array: np.array, initial_slice : int, intensity_threshold: int = 3, leg_intensity_threshold: int = 50, min_sequence_lenght: int = 10):
    """FIRST STEP"""
    # Extract the number of pixel greater than the threshold for each slice
    num_pixels_arr = []
    array_leg = array[0:initial_slice+1,:,:]
    for z in range(array_leg.shape[0]):
        slice_array = array_leg[z,:,:]
        num_pixels_arr.append((slice_array > leg_intensity_threshold).sum())
    
    num_pixels_arr = np.array(num_pixels_arr).reshape(-1,1)
    labels = kmeans_labels(num_pixels_arr)
    
    leg_slice = find_first_cluster1_sequence(labels, min_length=min_sequence_lenght, reverse=False) + 20


    """SECOND STEP"""
    final_array = array[leg_slice:initial_slice+1,:,:]
    num_pixels_arr = []
    for z in range(final_array.shape[0]):
        slice_array = final_array[z,:,:]
        num_pixels_arr.append((slice_array > intensity_threshold).sum())
        
    num_pixels_arr = np.array(num_pixels_arr).reshape(-1,1)
    labels = kmeans_labels(num_pixels_arr)
    
    return leg_slice, find_first_cluster1_sequence(labels, min_length=min_sequence_lenght) + leg_slice
    
def extract_initial_slice(array: np.array, intensity_threshold: int = 3, min_sequence_lenght: int = 10):
    # Extract the number of pixel greater than the threshold for each slice
    num_pixels_arr = []
    for z in range(array.shape[0]):
        slice_array = array[z,:,:]
        num_pixels_arr.append((slice_array > intensity_threshold).sum())
        
    num_pixels_arr = np.array(num_pixels_arr).reshape(-1,1)
    labels = kmeans_labels(num_pixels_arr)
    
    return find_first_cluster1_sequence(labels, min_length=min_sequence_lenght)

def kmeans_labels(array: np.array, n_clusters: int = 2, random_state: int = 42):
    """
    Fit a KMeans model and relabel cluster indices in ascending order of cluster means.
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    kmeans.fit(array)

    labels = kmeans.labels_
    cluster_means = kmeans.cluster_centers_.flatten()
    sorted_indices = np.argsort(cluster_means)
    label_map = {old: new for new, old in enumerate(sorted_indices)}
    relabelled = np.vectorize(label_map.get)(labels)

    return relabelled

def find_first_cluster1_sequence(labels, min_length=10, reverse= True):
    labels = np.array(labels)
    if reverse:
        labels = labels[::-1]

    count = 0
    start_in = None

    for i, val in enumerate(labels):
        if val == 1:
            count += 1
            if count == min_length:
                start_in = i - min_length + 1
                break
        else:
            count = 0

    if start_in is None:
        return None

    if reverse:
        start_in = len(labels) - (start_in + 1)
    return start_in

def get_pet_slice_index_from_ct_slice(ct_path, pet_path, ct_slice_index):
    """
    Given a CT slice index, return the corresponding PET slice index based on physical coordinates.

    Parameters:
        ct_path (str): Path to the CT image.
        pet_path (str): Path to the PET image.
        ct_slice_index (int): Slice index in CT image.

    Returns:
        int: Corresponding slice index in PET image.
    """
    # Set image type
    pixel_type_in = itk.F
    dimensions = 3
    image_type_in = itk.Image[pixel_type_in, dimensions]

    # Read CT image
    ct_reader = itk.ImageFileReader[image_type_in].New()
    ct_reader.SetFileName(str(Path(ct_path)))
    ct_reader.Update()
    ct_image = ct_reader.GetOutput()

    # Read PET image
    pet_reader = itk.ImageFileReader[image_type_in].New()
    pet_reader.SetFileName(str(Path(pet_path)))
    pet_reader.Update()
    pet_image = pet_reader.GetOutput()

    # Get spacing, origin, and direction
    ct_spacing = ct_image.GetSpacing()
    ct_origin = ct_image.GetOrigin()
    ct_direction = ct_image.GetDirection()

    pet_spacing = pet_image.GetSpacing()
    pet_origin = pet_image.GetOrigin()
    pet_direction = pet_image.GetDirection()

    # Compute world Z coordinate from CT slice
    z_world = ct_origin[2] + ct_slice_index * ct_spacing[2] * ct_direction[8]  # direction[2][2]

    # Map Z world coordinate to PET index
    pet_slice_index = int(round((z_world - pet_origin[2]) / (pet_spacing[2] * pet_direction[8])))

    return pet_slice_index