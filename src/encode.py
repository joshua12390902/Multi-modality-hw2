#!/usr/bin/env python3
"""
Medical Image Encoder - Lossy compression for medical images

Usage:
    python encode.py --input <input_file> --output <output_file> --quality <1-100>
"""

import argparse
import numpy as np
from pathlib import Path
import sys

from utils import read_dicom, pad_image
from dct_transform import (
    create_quantization_matrix, block_dct_encode, zigzag_flatten
)
from huffman_coding import encode_coefficients
from bitstream import pack_bitstream


def encode_image(input_path, output_path, quality=75, block_size=8):
    """
    Encode medical image to compressed format
    
    Args:
        input_path: Path to input DICOM file
        output_path: Path to output compressed file
        quality: Quality parameter (1-100, higher = better)
        block_size: DCT block size
    """
    print(f"Encoding {input_path}...")
    print(f"Quality: {quality}")
    
    # Read input image
    try:
        pixels, metadata = read_dicom(input_path)
        print(f"Image size: {metadata['width']}x{metadata['height']}")
        print(f"Bit depth: {metadata['bit_depth']}")
        print(f"Modality: {metadata['modality']}")
    except Exception as e:
        print(f"Error reading input: {e}")
        sys.exit(1)
    
    # Extract parameters
    width = metadata['width']
    height = metadata['height']
    bit_depth = metadata['bit_depth']
    
    # Pad image to block size
    padded_image, original_shape = pad_image(pixels, block_size)
    padded_height, padded_width = padded_image.shape
    
    # Create quantization matrix
    quant_matrix = create_quantization_matrix(quality, block_size, bit_depth)
    
    # Apply block DCT encoding
    print("Applying DCT transform...")
    dct_blocks = block_dct_encode(padded_image, quant_matrix, block_size)
    
    # Flatten blocks in zigzag order
    print("Flattening coefficients...")
    coeffs_list = [zigzag_flatten(block) for block in dct_blocks]
    
    # Huffman encoding
    print("Applying Huffman encoding...")
    encoded_data, huffman_table, num_bits = encode_coefficients(coeffs_list)
    
    # Pack into bitstream
    print("Packing bitstream...")
    bitstream = pack_bitstream(
        width=width,
        height=height,
        bit_depth=bit_depth,
        block_size=block_size,
        quality=quality,
        quant_matrix=quant_matrix,
        huffman_table=huffman_table,
        encoded_data=encoded_data,
        num_bits=num_bits
    )
    
    # Write to file
    with open(output_path, 'wb') as f:
        f.write(bitstream)
    
    # Report compression stats
    original_size = width * height * 2  # 16-bit pixels
    compressed_size = len(bitstream)
    compression_ratio = original_size / compressed_size
    bpp = (compressed_size * 8) / (width * height)
    
    print(f"\n{'='*50}")
    print(f"Encoding complete!")
    print(f"Original size: {original_size:,} bytes")
    print(f"Compressed size: {compressed_size:,} bytes")
    print(f"Compression ratio: {compression_ratio:.2f}:1")
    print(f"Bits per pixel: {bpp:.3f}")
    print(f"Output file: {output_path}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(
        description='Encode medical image to compressed format'
    )
    parser.add_argument('--input', required=True, help='Input DICOM file')
    parser.add_argument('--output', required=True, help='Output compressed file')
    parser.add_argument('--quality', type=int, default=75,
                       help='Quality parameter (1-100, default: 75)')
    parser.add_argument('--block-size', type=int, default=8,
                       help='DCT block size (default: 8)')
    
    args = parser.parse_args()
    
    # Validate quality
    if not 1 <= args.quality <= 100:
        print("Error: Quality must be between 1 and 100")
        sys.exit(1)
    
    # Check input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Encode
    encode_image(args.input, args.output, args.quality, args.block_size)


if __name__ == '__main__':
    main()
