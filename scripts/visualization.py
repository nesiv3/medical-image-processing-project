import numpy as np
import matplotlib.pyplot as plt

def visualize_array(arr, cmap='viridis', title='Array Visualization'):
    """
    Visualizes a 2D numpy array using imshow.

    Parameters:
    - arr: 2D numpy array
    - cmap: Colormap for visualization (default: 'viridis')
    - title: Title of the plot
    """
    if arr.ndim != 2:
        raise ValueError("Input array must be 2D")

    plt.figure(figsize=(6, 6))
    plt.imshow(arr, cmap=cmap)
    plt.colorbar(label='Value')
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.tight_layout()
    plt.show()