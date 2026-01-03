#!/usr/bin/env python3
"""
Evaluate codec on real Medimodel Human_Skull_2 CT data
Uses SimpleITK to handle JPEG Lossless DICOM
"""

import os
import sys
import json
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
from scipy.ndimage import sobel

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dct_transform import dct2d, idct2d, create_quantization_matrix, quantize, dequantize, zigzag_flatten, zigzag_unflatten
from huffman_coding import build_huffman_tree, generate_huffman_codes, encode_huffman, decode_huffman, serialize_huffman_table, deserialize_huffman_table
from bitstream import pack_bitstream, unpack_bitstream

def read_dicom_sitk(dicom_path):
    """
    Read DICOM file using SimpleITK (handles JPEG Lossless)
    """
    try:
        reader = sitk.ImageFileReader()
        reader.SetFileName(str(dicom_path))
        image = reader.Execute()
        
        # Convert to numpy array (shape: [slices, height, width])
        pixel_array = sitk.GetArrayFromImage(image)
        
        # If 3D, take first slice; if 2D, squeeze
        if pixel_array.ndim == 3:
            pixel_array = pixel_array[0]
        elif pixel_array.ndim == 2:
            pass
        else:
            pixel_array = pixel_array.squeeze()
        
        return pixel_array.astype(np.float32)
        
    except Exception as e:
        print(f"Error reading {dicom_path}: {e}")
        return None

def encode_image_direct(image, quality=50):
    """
    Encode image array directly (no file I/O)
    Returns: compressed bitstream bytes
    """
    height, width = image.shape
    block_size = 8
    bit_depth = 16

    # Pad image
    pad_h = (block_size - height % block_size) % block_size
    pad_w = (block_size - width % block_size) % block_size
    padded = np.pad(image, ((0, pad_h), (0, pad_w)), mode='edge')

    # Create quantization matrix
    quant_matrix = create_quantization_matrix(quality, block_size, bit_depth)

    # Process blocks: DCT -> quantize -> zigzag
    all_coeffs = []
    for i in range(0, padded.shape[0], block_size):
        for j in range(0, padded.shape[1], block_size):
            block = padded[i:i+block_size, j:j+block_size]

            dct_block = dct2d(block)
            quant_block = quantize(dct_block, quant_matrix)
            coeffs = zigzag_flatten(quant_block)
            all_coeffs.extend(coeffs)

    # Huffman encode
    from collections import Counter
    symbols_freq = Counter(all_coeffs)
    huffman_tree = build_huffman_tree(symbols_freq)
    huffman_codes = generate_huffman_codes(huffman_tree)
    encoded_bits = encode_huffman(all_coeffs, huffman_codes)
    num_bits = len(encoded_bits)

    # Serialize Huffman table
    huffman_table = serialize_huffman_table(huffman_codes)

    # Convert bitstring to bytes
    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bits), 8):
        byte_str = encoded_bits[i:i+8].ljust(8, '0')
        encoded_bytes.append(int(byte_str, 2))

    # Pack bitstream
    bitstream = pack_bitstream(
        width, height, bit_depth, block_size, quality,
        quant_matrix, huffman_table, bytes(encoded_bytes), num_bits
    )

    return bitstream

def decode_image_direct(bitstream):
    """
    Decode bitstream directly (no file I/O)
    Returns: reconstructed image array
    """
    # Unpack bitstream
    params = unpack_bitstream(bitstream)
    if params is None:
        return None
    
    width = params['width']
    height = params['height']
    bit_depth = params['bit_depth']
    block_size = params['block_size']
    quality = params['quality']
    quant_matrix = params['quant_matrix']
    huffman_table = params['huffman_table']
    encoded_data = params['encoded_data']
    num_bits = params['num_bits']
    
    # Deserialize Huffman codes
    huffman_codes, _ = deserialize_huffman_table(huffman_table)
    
    # Convert bytes to bitstring
    bitstring = ''.join(f'{byte:08b}' for byte in encoded_data)[:num_bits]
    
    # Decode Huffman
    decoded_coeffs = []
    current = ''
    code_to_symbol = {code: symbol for symbol, code in huffman_codes.items()}
    
    for bit in bitstring:
        current += bit
        if current in code_to_symbol:
            decoded_coeffs.append(code_to_symbol[current])
            current = ''
    
    coeffs = decoded_coeffs
    
    # Reconstruct blocks
    pad_h = (block_size - height % block_size) % block_size
    pad_w = (block_size - width % block_size) % block_size
    padded_h = height + pad_h
    padded_w = width + pad_w
    
    reconstructed = np.zeros((padded_h, padded_w), dtype=np.float32)
    
    num_blocks_h = padded_h // block_size
    num_blocks_w = padded_w // block_size
    
    coeff_idx = 0
    for i in range(num_blocks_h):
        for j in range(num_blocks_w):
            # Get coefficients for this block
            block_coeffs = coeffs[coeff_idx:coeff_idx + block_size * block_size]
            coeff_idx += block_size * block_size
            
            # Inverse zigzag
            quant_block = zigzag_unflatten(np.array(block_coeffs), block_size)
            
            # Dequantize
            dct_block = dequantize(quant_block, quant_matrix)
            
            # IDCT
            block = idct2d(dct_block)
            
            reconstructed[i*block_size:(i+1)*block_size, 
                         j*block_size:(j+1)*block_size] = block
    
    # Unpad
    reconstructed = reconstructed[:height, :width]
    
    return reconstructed

def calculate_metrics(original, reconstructed):
    """Calculate RMSE, PSNR, SSIM, and edge-preservation RMSE/PSNR"""
    rmse = np.sqrt(np.mean((original - reconstructed) ** 2))
    max_val = 65535.0  # 16-bit
    psnr = 20 * np.log10(max_val / rmse) if rmse > 0 else 100.0

    # SSIM expects data range and float64
    ssim_val = ssim(original, reconstructed, data_range=max_val)

    # Edge preservation: Sobel magnitude
    def sobel_mag(x):
        gx = sobel(x, axis=0)
        gy = sobel(x, axis=1)
        return np.hypot(gx, gy)

    orig_edge = sobel_mag(original)
    recon_edge = sobel_mag(reconstructed)
    edge_rmse = np.sqrt(np.mean((orig_edge - recon_edge) ** 2))
    edge_max = np.max(orig_edge) if np.max(orig_edge) > 0 else 1.0
    edge_psnr = 20 * np.log10(edge_max / edge_rmse) if edge_rmse > 0 else 100.0

    return rmse, psnr, ssim_val, edge_rmse, edge_psnr

def evaluate_real_medimodel():
    """
    Evaluate codec on real Medimodel CT data
    """
    dicom_dir = '/workspace/MMIP_hw2/2_skull_ct/DICOM_dcm'
    output_dir = '/workspace/MMIP_hw2/results_real'
    os.makedirs(output_dir, exist_ok=True)
    
    # Select representative slices
    slice_indices = [50, 100, 150, 200, 250]
    quality_levels = [30, 60, 90]
    
    results = {
        'dataset': 'Medimodel Human_Skull_2 CT',
        'source': '512×512, 16-bit, JPEG Lossless DICOM',
        'slices_evaluated': [],
        'quality_levels': quality_levels,
        'results': []
    }
    
    print(f"Evaluating {len(slice_indices)} slices at {len(quality_levels)} quality levels...")
    print(f"Output directory: {output_dir}\n")
    
    for idx in slice_indices:
        dicom_file = f'I{idx}.dcm'
        dicom_path = os.path.join(dicom_dir, dicom_file)
        
        if not os.path.exists(dicom_path):
            print(f"⚠ Skipping {dicom_file} (not found)")
            continue
        
        print(f"Processing {dicom_file}...")
        
        # Read DICOM
        image = read_dicom_sitk(dicom_path)
        if image is None:
            print(f"  ✗ Failed to read")
            continue
        
        print(f"  Shape: {image.shape}, Range: [{image.min():.0f}, {image.max():.0f}]")
        
        slice_result = {
            'slice': dicom_file,
            'shape': [int(s) for s in image.shape],
            'value_range': [float(image.min()), float(image.max())],
            'qualities': {}
        }
        
        for quality in quality_levels:
            # Encode
            bitstream = encode_image_direct(image, quality)
            compressed_size = len(bitstream)
            
            # Decode
            reconstructed = decode_image_direct(bitstream)
            
            # Calculate metrics
            rmse, psnr, ssim_val, edge_rmse, edge_psnr = calculate_metrics(image, reconstructed)
            
            # Calculate compression metrics
            original_size = image.size * 2  # 16-bit = 2 bytes per pixel
            bpp = (compressed_size * 8) / image.size
            ratio = original_size / compressed_size
            
            slice_result['qualities'][str(quality)] = {
                'compressed_bytes': int(compressed_size),
                'bits_per_pixel': float(bpp),
                'compression_ratio': float(ratio),
                'rmse': float(rmse),
                'psnr_db': float(psnr),
                'ssim': float(ssim_val),
                'edge_rmse': float(edge_rmse),
                'edge_psnr_db': float(edge_psnr)
            }
            
            print(f"    Q={quality}: {compressed_size:,} bytes, {bpp:.3f} bpp, {ratio:.2f}:1, PSNR={psnr:.2f} dB")
        
        results['results'].append(slice_result)
        results['slices_evaluated'].append(dicom_file)
    
    # Save results
    results_file = os.path.join(output_dir, 'medimodel_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Evaluation complete!")
    print(f"Results saved to: {results_file}")
    
    # Generate summary table
    print("\n" + "="*80)
    print("SUMMARY: Average Performance Across All Slices")
    print("="*80)

    for quality in quality_levels:
        metrics = [r['qualities'][str(quality)] for r in results['results']]
        avg_bpp = np.mean([m['bits_per_pixel'] for m in metrics])
        avg_ratio = np.mean([m['compression_ratio'] for m in metrics])
        avg_psnr = np.mean([m['psnr_db'] for m in metrics])
        avg_ssim = np.mean([m['ssim'] for m in metrics])
        avg_edge_psnr = np.mean([m['edge_psnr_db'] for m in metrics])
        avg_size = np.mean([m['compressed_bytes'] for m in metrics])

        print(f"Quality {quality:2d}: {avg_size:>8.0f} bytes | {avg_bpp:>5.3f} bpp | "
              f"{avg_ratio:>5.2f}:1 | PSNR {avg_psnr:>5.2f} dB | SSIM {avg_ssim:>5.4f} | Edge PSNR {avg_edge_psnr:>5.2f} dB")
    
    return results

if __name__ == '__main__':
    evaluate_real_medimodel()
