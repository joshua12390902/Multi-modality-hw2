"""
Utility functions for medical image codec
"""
import numpy as np
import pydicom
from pathlib import Path


def read_dicom(filepath):
    """
    Read DICOM file and return pixel array with metadata
    
    Args:
        filepath: Path to DICOM file
        
    Returns:
        pixels: numpy array of pixel values
        metadata: dict with bit_depth, width, height
    """
    dcm = pydicom.dcmread(filepath)
    pixels = dcm.pixel_array
    
    metadata = {
        'width': pixels.shape[1],
        'height': pixels.shape[0],
        'bit_depth': dcm.BitsStored if hasattr(dcm, 'BitsStored') else 16,
        'modality': dcm.Modality if hasattr(dcm, 'Modality') else 'UNKNOWN'
    }
    
    return pixels.astype(np.int32), metadata


def save_raw_image(pixels, filepath, bit_depth=16):
    """Save image as raw binary file"""
    # Normalize to bit depth range
    max_val = (1 << bit_depth) - 1
    pixels_clipped = np.clip(pixels, 0, max_val)
    
    # Save as uint16 for 12-16 bit images
    pixels_clipped.astype(np.uint16).tofile(filepath)
    

def load_raw_image(filepath, width, height):
    """Load raw binary image file"""
    pixels = np.fromfile(filepath, dtype=np.uint16)
    return pixels.reshape(height, width)


def calculate_metrics(original, reconstructed, bit_depth=16):
    """
    Calculate rate-distortion metrics
    
    Args:
        original: Original image array
        reconstructed: Reconstructed image array  
        bit_depth: Bit depth of images
        
    Returns:
        dict with RMSE, PSNR
    """
    # Ensure same shape
    assert original.shape == reconstructed.shape, "Image dimensions must match"
    
    # Calculate RMSE
    mse = np.mean((original.astype(np.float64) - reconstructed.astype(np.float64)) ** 2)
    rmse = np.sqrt(mse)
    
    # Calculate PSNR
    max_val = (1 << bit_depth) - 1
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = 20 * np.log10(max_val / rmse)
    
    return {
        'RMSE': rmse,
        'PSNR': psnr,
        'MSE': mse
    }


def calculate_rate_metrics(compressed_size, width, height, original_size=None):
    """
    Calculate rate metrics
    
    Args:
        compressed_size: Size in bytes
        width, height: Image dimensions
        original_size: Original file size in bytes (optional)
        
    Returns:
        dict with bpp, compression_ratio
    """
    num_pixels = width * height
    bpp = (compressed_size * 8) / num_pixels
    
    metrics = {
        'compressed_bytes': compressed_size,
        'bpp': bpp
    }
    
    if original_size:
        metrics['compression_ratio'] = original_size / compressed_size
    
    return metrics


def pad_image(image, block_size=8):
    """
    Pad image to be divisible by block_size
    
    Args:
        image: Input image
        block_size: Block size (default 8)
        
    Returns:
        padded_image, original_shape
    """
    height, width = image.shape
    
    # Calculate padding
    pad_h = (block_size - height % block_size) % block_size
    pad_w = (block_size - width % block_size) % block_size
    
    if pad_h == 0 and pad_w == 0:
        return image, (height, width)
    
    # Pad with edge values
    padded = np.pad(image, ((0, pad_h), (0, pad_w)), mode='edge')
    
    return padded, (height, width)


def unpad_image(image, original_shape):
    """Remove padding from image"""
    height, width = original_shape
    return image[:height, :width]
