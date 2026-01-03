#!/usr/bin/env python3
"""
Generate synthetic 16-bit medical test images
"""
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
import datetime
from pathlib import Path


def create_synthetic_ct(width=512, height=512, bit_depth=16):
    """
    Create synthetic CT-like image with various structures
    
    Returns:
        2D numpy array with 16-bit values
    """
    # Create base image
    image = np.zeros((height, width), dtype=np.uint16)
    
    # Background (air)
    image[:] = 0
    
    # Soft tissue circle (body outline)
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 3
    y, x = np.ogrid[:height, :width]
    mask_body = (x - center_x)**2 + (y - center_y)**2 <= radius**2
    image[mask_body] = 2000  # Soft tissue HU ~ 2000 in raw units
    
    # Bone structures (ribs)
    for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
        rib_x = int(center_x + radius * 0.7 * np.cos(angle))
        rib_y = int(center_y + radius * 0.7 * np.sin(angle))
        rib_radius = 20
        mask_rib = (x - rib_x)**2 + (y - rib_y)**2 <= rib_radius**2
        image[mask_rib] = 4000  # Bone HU ~ 4000 in raw units
    
    # Lung-like regions (dark circles)
    lung_offset = radius // 3
    for dx in [-lung_offset, lung_offset]:
        lung_x = center_x + dx
        lung_y = center_y - lung_offset // 2
        lung_radius = radius // 4
        mask_lung = (x - lung_x)**2 + (y - lung_y)**2 <= lung_radius**2
        image[mask_lung] = 800  # Lung HU ~ 800 in raw units
    
    # Heart-like structure
    heart_x = center_x
    heart_y = center_y + lung_offset // 2
    heart_radius = radius // 5
    mask_heart = (x - heart_x)**2 + (y - heart_y)**2 <= heart_radius**2
    image[mask_heart] = 2200  # Heart/muscle
    
    # Add some Gaussian noise
    noise = np.random.normal(0, 50, (height, width))
    image = image.astype(np.float32) + noise
    image = np.clip(image, 0, (1 << bit_depth) - 1)
    
    return image.astype(np.uint16)


def save_as_dicom(image, filepath, modality='CT'):
    """
    Save numpy array as DICOM file
    
    Args:
        image: 2D numpy array
        filepath: Output path
        modality: DICOM modality (CT, MR, etc.)
    """
    # Create file meta information
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = '1.2.3.4.5.6.7.8.9'
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    
    # Create DICOM dataset
    ds = FileDataset(filepath, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # Patient info
    ds.PatientName = "Test^Patient"
    ds.PatientID = "TEST001"
    
    # Study info
    ds.StudyDate = datetime.datetime.now().strftime('%Y%m%d')
    ds.StudyTime = datetime.datetime.now().strftime('%H%M%S')
    ds.StudyInstanceUID = '1.2.3.4.5.6.7.8'
    ds.SeriesInstanceUID = '1.2.3.4.5.6.7.8.9'
    ds.SOPInstanceUID = '1.2.3.4.5.6.7.8.9.10'
    
    # Image info
    ds.Modality = modality
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    
    # Image pixel data
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.Rows = image.shape[0]
    ds.Columns = image.shape[1]
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0  # Unsigned
    
    ds.PixelData = image.tobytes()
    
    # Save
    ds.save_as(filepath, write_like_original=False)
    print(f"Saved DICOM: {filepath}")


def main():
    """Generate test images"""
    # Create output directory
    test_dir = Path('test_data')
    test_dir.mkdir(exist_ok=True)
    
    print("Generating synthetic test images...")
    
    # Generate CT images at different sizes
    configs = [
        {'name': 'ct_512x512.dcm', 'width': 512, 'height': 512},
        {'name': 'ct_256x256.dcm', 'width': 256, 'height': 256},
        {'name': 'ct_1024x1024.dcm', 'width': 1024, 'height': 1024},
    ]
    
    for config in configs:
        image = create_synthetic_ct(config['width'], config['height'])
        filepath = test_dir / config['name']
        save_as_dicom(image, filepath)
        print(f"  Size: {config['width']}x{config['height']}, Mean: {image.mean():.1f}, Std: {image.std():.1f}")
    
    print(f"\n✓ Generated {len(configs)} test images in {test_dir}/")


if __name__ == '__main__':
    main()
