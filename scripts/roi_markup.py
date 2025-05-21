import numpy as np

# Get the volume node
volumeNode = [n for n in getNodesByClass('vtkMRMLScalarVolumeNode') if "PET" in n.GetName()][0]

# Define the ROI bounds in IJK
ijk_min = np.array([54, 100, 139])
ijk_max = np.array([59, 105, 144])

# Compute center and size in IJK
center_ijk = (ijk_min + ijk_max) / 2
size_ijk = ijk_max - ijk_min

# Convert to RAS
ijk_to_ras = vtk.vtkMatrix4x4()
volumeNode.GetIJKToRASMatrix(ijk_to_ras)

def ijk_to_ras_func(ijk):
    ras = [0, 0, 0, 1]
    ijk_hom = list(ijk) + [1]
    ijk_to_ras.MultiplyPoint(ijk_hom, ras)
    return np.array(ras[:3])

center_ras = ijk_to_ras_func(center_ijk)
corner_ras = ijk_to_ras_func(ijk_min)
size_ras = np.abs(ijk_to_ras_func(ijk_max) - corner_ras)

# Create ROI node
roi = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode", "ROI_Tumor")
roi.SetCenter(*center_ras)
roi.SetSize(*size_ras)

print("✅ ROI created in Slicer!")