#!/usr/bin/env python3
"""
Medical Image Decoder - Decompress medical images

Usage:
    python decode.py --input <input_file> --output <output_file>
"""

import argparse
import numpy as np
from pathlib import Path
import sys

from utils import save_raw_image, unpad_image
from dct_transform import block_dct_decode, zigzag_unflatten
from huffman_coding import decode_coefficients
from bitstream import unpack_bitstream


def decode_image(input_path, output_path):
    """
    Decode compressed medical image
    
    Args:
        input_path: Path to compressed file
        output_path: Path to output raw image file
    """
    print(f"Decoding {input_path}...")
    
    # Read bitstream
    try:
        with open(input_path, 'rb') as f:
            bitstream_data = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Unpack bitstream
    try:
        params = unpack_bitstream(bitstream_data)
    except Exception as e:
        print(f"Error: Malformed bitstream - {e}")
        sys.exit(1)
    
    # Extract parameters
    width = params['width']
    height = params['height']
    bit_depth = params['bit_depth']
    block_size = params['block_size']
    quality = params['quality']
    quant_matrix = params['quant_matrix']
    huffman_table = params['huffman_table']
    encoded_data = params['encoded_data']
    num_bits = params['num_bits']
    
    print(f"Image size: {width}x{height}")
    print(f"Bit depth: {bit_depth}")
    print(f"Quality: {quality}")
    print(f"Block size: {block_size}")
    
    # Calculate padded dimensions
    padded_height = ((height + block_size - 1) // block_size) * block_size
    padded_width = ((width + block_size - 1) // block_size) * block_size
    num_blocks = (padded_height // block_size) * (padded_width // block_size)
    num_coeffs = num_blocks * block_size * block_size
    
    print(f"Number of blocks: {num_blocks}")
    
    # Huffman decoding
    print("Applying Huffman decoding...")
    coeffs_flat = decode_coefficients(encoded_data, huffman_table, num_bits, num_coeffs)
    
    # Reshape into blocks
    print("Reconstructing blocks...")
    dct_blocks = []
    for i in range(num_blocks):
        start_idx = i * block_size * block_size
        end_idx = start_idx + block_size * block_size
        block_flat = coeffs_flat[start_idx:end_idx]
        
        # Convert to numpy array
        block_flat_array = np.array(block_flat, dtype=np.int16)
        
        # Unflatten from zigzag order
        block = zigzag_unflatten(block_flat_array, block_size)
        dct_blocks.append(block)
    
    # Apply inverse DCT
    print("Applying inverse DCT...")
    reconstructed_padded = block_dct_decode(
        dct_blocks, quant_matrix, padded_height, padded_width, block_size
    )
    
    # Remove padding
    reconstructed = unpad_image(reconstructed_padded, (height, width))
    
    # Clip to valid range
    max_val = (1 << bit_depth) - 1
    reconstructed = np.clip(reconstructed, 0, max_val).astype(np.int32)
    
    # Save output
    print(f"Saving to {output_path}...")
    save_raw_image(reconstructed, output_path, bit_depth)
    
    print(f"\n{'='*50}")
    print(f"Decoding complete!")
    print(f"Output file: {output_path}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(
        description='Decode compressed medical image'
    )
    parser.add_argument('--input', required=True, help='Input compressed file')
    parser.add_argument('--output', required=True, help='Output raw image file')
    
    args = parser.parse_args()
    
    # Check input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Decode
    decode_image(args.input, args.output)


if __name__ == '__main__':
    main()
