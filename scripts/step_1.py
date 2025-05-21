from pathlib import Path
from typing import Union
import itk
import os
import time

def histogram_equalization_filter(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    dimensions: int = 3,
    median_filter_rad: int = 1
) -> tuple:
    # Define pixel types
    pixel_type_in = itk.F
    pixel_type_out = itk.UC
    image_type_in = itk.Image[pixel_type_in, dimensions]
    image_type_out = itk.Image[pixel_type_out, dimensions]

    # Step 1: Read the image as float
    reader = itk.ImageFileReader[image_type_in].New()
    reader.SetFileName(str(input_file))
    reader.Update()

    image = reader.GetOutput()
    size = itk.size(image)

    # Step 2: Rescale to unsigned short
    rescaler = itk.RescaleIntensityImageFilter[image_type_in, image_type_out].New()
    rescaler.SetInput(image)
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)
    rescaler.Update()

    rescaled_image = rescaler.GetOutput()

    median_filter = itk.MedianImageFilter[image_type_out, image_type_out].New()
    median_filter.SetInput(rescaled_image)

    # Set radius
    radius = itk.Size[dimensions]()
    for i in range(dimensions):
        radius[i] = median_filter_rad
    
    median_filter.SetRadius(radius)
    median_filter.Update()

    # # Step 3: Apply adaptive histogram equalization
    # equalizer = itk.AdaptiveHistogramEqualizationImageFilter[image_type_out].New()
    # equalizer.SetAlpha(0)
    # equalizer.SetBeta(0)
    # equalizer.SetRadius(72)
    # equalizer.SetInput(rescaled_image)
    # equalizer.Update()

    # final_image = median_filter.GetOutput()
    final_image = rescaled_image
    final_image = median_filter.GetOutput()

    # Step 4: Write result
    writer = itk.ImageFileWriter[image_type_out].New()
    writer.SetFileName(str(output_file))
    writer.SetInput(final_image)
    writer.Update()

    return tuple(size)


if __name__ == "__main__":
    BASE_PATH = Path(os.getcwd()).parent
    names = ["10", "11", "14"]
    name = names[0]
    extension = "nii.gz"
    input_image = BASE_PATH / f"train_nifti/{name}/p{name}_PET_enhanced.{extension}"
    output_image = BASE_PATH / f"train_nifti/{name}/p{name}_PET_enhanced_median.{extension}"
    
    start_time = time.time()
    
    size = histogram_equalization_filter(input_image, output_image)
    
    # Calculate total time
    total_time = time.time() - start_time
    print(f"Total time taken: {total_time:.2f} seconds")
