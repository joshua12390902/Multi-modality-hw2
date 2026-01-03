"""
Bitstream format for medical image codec

Format:
- Magic number (4 bytes): 'MEDC'
- Version (1 byte): 0x01
- Width (2 bytes): uint16
- Height (2 bytes): uint16
- Bit depth (1 byte): uint8
- Block size (1 byte): uint8
- Quality (1 byte): uint8
- Quantization matrix size (2 bytes): uint16
- Quantization matrix (variable): uint16 array
- Huffman table size (2 bytes): uint16
- Huffman table (variable): serialized table
- Number of encoded bits (4 bytes): uint32
- Encoded data size (4 bytes): uint32
- Encoded data (variable): bytes
"""

import struct
import numpy as np


MAGIC_NUMBER = b'MEDC'
VERSION = 0x01


def pack_bitstream(width, height, bit_depth, block_size, quality, 
                   quant_matrix, huffman_table, encoded_data, num_bits):
    """
    Pack all data into bitstream format
    
    Args:
        width, height: Image dimensions
        bit_depth: Bit depth of image
        block_size: DCT block size
        quality: Quality parameter
        quant_matrix: Quantization matrix (2D array)
        huffman_table: Serialized Huffman table (bytes)
        encoded_data: Encoded coefficient data (bytes)
        num_bits: Number of bits in encoded data
        
    Returns:
        bytes
    """
    data = bytearray()
    
    # Header
    data.extend(MAGIC_NUMBER)
    data.append(VERSION)
    data.extend(struct.pack('>H', width))   # Big-endian uint16
    data.extend(struct.pack('>H', height))
    data.append(bit_depth)
    data.append(block_size)
    data.append(quality)
    
    # Quantization matrix
    quant_flat = quant_matrix.flatten()
    data.extend(struct.pack('>H', len(quant_flat)))
    for val in quant_flat:
        data.extend(struct.pack('>H', int(val)))
    
    # Huffman table
    data.extend(struct.pack('>H', len(huffman_table)))
    data.extend(huffman_table)
    
    # Encoded data
    data.extend(struct.pack('>I', num_bits))  # uint32
    data.extend(struct.pack('>I', len(encoded_data)))
    data.extend(encoded_data)
    
    return bytes(data)


def unpack_bitstream(data):
    """
    Unpack bitstream and extract all components
    
    Args:
        data: bytes
        
    Returns:
        dict with all parameters and encoded data
    """
    offset = 0
    
    # Check magic number
    magic = data[offset:offset+4]
    if magic != MAGIC_NUMBER:
        raise ValueError(f"Invalid magic number: {magic}")
    offset += 4
    
    # Version
    version = data[offset]
    if version != VERSION:
        raise ValueError(f"Unsupported version: {version}")
    offset += 1
    
    # Image parameters
    width = struct.unpack('>H', data[offset:offset+2])[0]
    offset += 2
    height = struct.unpack('>H', data[offset:offset+2])[0]
    offset += 2
    bit_depth = data[offset]
    offset += 1
    block_size = data[offset]
    offset += 1
    quality = data[offset]
    offset += 1
    
    # Quantization matrix
    quant_size = struct.unpack('>H', data[offset:offset+2])[0]
    offset += 2
    quant_flat = []
    for _ in range(quant_size):
        val = struct.unpack('>H', data[offset:offset+2])[0]
        quant_flat.append(val)
        offset += 2
    quant_matrix = np.array(quant_flat, dtype=np.uint16).reshape(block_size, block_size)
    
    # Huffman table
    huffman_size = struct.unpack('>H', data[offset:offset+2])[0]
    offset += 2
    huffman_table = data[offset:offset+huffman_size]
    offset += huffman_size
    
    # Encoded data
    num_bits = struct.unpack('>I', data[offset:offset+4])[0]
    offset += 4
    encoded_size = struct.unpack('>I', data[offset:offset+4])[0]
    offset += 4
    encoded_data = data[offset:offset+encoded_size]
    offset += encoded_size
    
    return {
        'width': width,
        'height': height,
        'bit_depth': bit_depth,
        'block_size': block_size,
        'quality': quality,
        'quant_matrix': quant_matrix,
        'huffman_table': huffman_table,
        'encoded_data': encoded_data,
        'num_bits': num_bits
    }


def validate_bitstream(filepath):
    """
    Validate bitstream file
    
    Args:
        filepath: Path to bitstream file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        unpack_bitstream(data)
        return True
    except Exception as e:
        print(f"Validation failed: {e}")
        return False
