import os
from pathlib import Path
from typing import List, Union, Tuple
import itk
from scripts.slices import extract_initial_slice, extract_final_slice

def tumor_segmentation(
    ct_path: Union[Path, str],
    pet_path: Union[Path, str],
    pet_output_path: Union[Path, str],
    pet_intensity_threshold: int = 2,
    pet_min_sequence_lenght: int = 10,
    ct_intensity_threshold: int = 50,
    ct_min_sequence_lenght: int = 10
) -> None:

    final_slice, _, initial_slice = \
    get_slices_range(
        ct_path,
        pet_path,
        pet_intensity_threshold=pet_intensity_threshold,
        pet_min_sequence_lenght=pet_min_sequence_lenght,
        ct_intensity_threshold=ct_intensity_threshold,
        ct_min_sequence_lenght=ct_min_sequence_lenght
    )
        
    dimensions = 3
    pixel_type_in = itk.F
    pixel_type_out = itk.UC
    image_type_in = itk.Image[pixel_type_in, dimensions]
    image_type_out = itk.Image[pixel_type_out, dimensions]

    reader = itk.ImageFileReader[image_type_in].New()
    reader.SetFileName(str(pet_path))
    reader.Update()
    image = reader.GetOutput()

    rescaler = itk.RescaleIntensityImageFilter[image_type_in, image_type_out].New()
    rescaler.SetInput(image)
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)
    rescaler.Update()
    image = rescaler.GetOutput()

    image_np_array = itk.GetArrayFromImage(image)
    image_np_array[:initial_slice, :, :] = 0
    image_np_array[final_slice+1:, :, :] = 0

    image_filtered = itk.GetImageFromArray(image_np_array)
    image_filtered.SetOrigin(image.GetOrigin())
    image_filtered.SetSpacing(image.GetSpacing())
    image_filtered.SetDirection(image.GetDirection())
    image_filtered.CopyInformation(image)

    rescaler = itk.RescaleIntensityImageFilter[image_type_out, image_type_out].New()
    rescaler.SetInput(image_filtered)
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)
    rescaler.Update()
    image_filtered = rescaler.GetOutput()

    # Step XX:
    itk.imwrite(image_filtered, str(pet_output_path))
    

def get_slices_range(
    ct_path: Union[Path, str],
    pet_path: Union[Path, str],
    pet_intensity_threshold: int = 2,
    pet_min_sequence_lenght: int = 10,
    ct_intensity_threshold: int = 50,
    ct_min_sequence_lenght: int = 10
) -> Tuple[int, int]:

    dimensions = 3
    pixel_type_in = itk.F
    pixel_type_out = itk.UC
    image_type_in = itk.Image[pixel_type_in, dimensions]
    image_type_out = itk.Image[pixel_type_out, dimensions]
    
    # Step 1: Read Pet and CT images as float
    reader_ct = itk.ImageFileReader[image_type_in].New()
    reader_ct.SetFileName(str(ct_path))
    reader_ct.Update()
    ct_image = reader_ct.GetOutput()

    reader_pet = itk.ImageFileReader[image_type_in].New()
    reader_pet.SetFileName(str(pet_path))
    reader_pet.Update()
    pet_image = reader_pet.GetOutput()

    # Step 2: Rescale PET image to 0-255 range (Unsigned Char)
    rescaler = itk.RescaleIntensityImageFilter[image_type_in, image_type_out].New()
    rescaler.SetInput(pet_image)
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)
    rescaler.Update()
    pet_image = rescaler.GetOutput()

    # Step 3: Get the initial slices that are assigned for the intensity-grater-cluster for both PET and CT image
    pet_np_array = itk.GetArrayFromImage(pet_image)
    pet_initial_slice = extract_initial_slice(pet_np_array, intensity_threshold=pet_intensity_threshold, min_sequence_lenght=pet_min_sequence_lenght)

    ct_np_array = itk.GetArrayFromImage(ct_image)
    ct_initial_slice = extract_initial_slice(ct_np_array, intensity_threshold=ct_intensity_threshold, min_sequence_lenght=ct_min_sequence_lenght)

    # Step 4: Transform CT slice to PET slice
    ct_spacing = ct_image.GetSpacing()
    ct_origin = ct_image.GetOrigin()
    ct_direction = ct_image.GetDirection().__array__()

    pet_spacing = pet_image.GetSpacing()
    pet_origin = pet_image.GetOrigin()
    pet_direction = pet_image.GetDirection().__array__()

    # Compute world Z coordinate from CT slice
    z_world = ct_origin[2] + ct_initial_slice * ct_spacing[2] * ct_direction[2][2]

    # Map Z world coordinate to PET index
    pet_final_slice = int(round((z_world - pet_origin[2]) / (pet_spacing[2] * pet_direction[2][2])))
    
    return (pet_initial_slice, ct_initial_slice, pet_final_slice)