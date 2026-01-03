"""
DCT transform and quantization for image compression
"""
import numpy as np
from scipy.fftpack import dct, idct


def dct2d(block):
    """
    2D DCT transform on a block
    
    Args:
        block: 2D numpy array (typically 8x8)
        
    Returns:
        DCT coefficients
    """
    return dct(dct(block.T, norm='ortho').T, norm='ortho')


def idct2d(block):
    """
    2D inverse DCT transform
    
    Args:
        block: DCT coefficients
        
    Returns:
        Reconstructed spatial block
    """
    return idct(idct(block.T, norm='ortho').T, norm='ortho')


def create_quantization_matrix(quality, block_size=8, bit_depth=16):
    """
    Create quantization matrix based on quality parameter
    
    Args:
        quality: Quality factor (1-100, higher = better quality)
        block_size: Size of transform block
        bit_depth: Bit depth of input image
        
    Returns:
        Quantization matrix
    """
    # Base quantization matrix (similar to JPEG but scaled for higher bit depth)
    base_matrix = np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68, 109, 103, 77],
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99]
    ])
    
    # Scale for higher bit depth (16-bit vs 8-bit)
    bit_scale = (1 << bit_depth) / 256.0
    
    # Quality scaling
    if quality < 50:
        scale = 5000 / quality
    else:
        scale = 200 - 2 * quality
    
    # Apply scaling
    quant_matrix = np.floor((base_matrix * scale * bit_scale + 50) / 100)
    quant_matrix = np.clip(quant_matrix, 1, 65535)
    
    return quant_matrix.astype(np.uint16)


def quantize(coeffs, quant_matrix):
    """
    Quantize DCT coefficients
    
    Args:
        coeffs: DCT coefficients
        quant_matrix: Quantization matrix
        
    Returns:
        Quantized coefficients
    """
    return np.round(coeffs / quant_matrix).astype(np.int16)


def dequantize(quantized_coeffs, quant_matrix):
    """
    Dequantize coefficients
    
    Args:
        quantized_coeffs: Quantized coefficients
        quant_matrix: Quantization matrix
        
    Returns:
        Dequantized coefficients
    """
    return quantized_coeffs * quant_matrix


def block_dct_encode(image, quant_matrix, block_size=8):
    """
    Apply block DCT encoding to entire image
    
    Args:
        image: Input image (must be padded to block_size)
        quant_matrix: Quantization matrix
        block_size: Size of blocks
        
    Returns:
        Quantized DCT coefficients for all blocks
    """
    height, width = image.shape
    
    # Initialize output
    dct_blocks = []
    
    # Process each block
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            block = image[i:i+block_size, j:j+block_size].astype(np.float64)
            
            # Apply DCT
            dct_block = dct2d(block)
            
            # Quantize
            quant_block = quantize(dct_block, quant_matrix)
            
            dct_blocks.append(quant_block)
    
    return dct_blocks


def block_dct_decode(dct_blocks, quant_matrix, height, width, block_size=8):
    """
    Decode image from quantized DCT blocks
    
    Args:
        dct_blocks: List of quantized DCT blocks
        quant_matrix: Quantization matrix
        height, width: Output image dimensions
        block_size: Size of blocks
        
    Returns:
        Reconstructed image
    """
    # Initialize output
    reconstructed = np.zeros((height, width), dtype=np.float64)
    
    block_idx = 0
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            # Dequantize
            dct_block = dequantize(dct_blocks[block_idx], quant_matrix)
            
            # Apply inverse DCT
            spatial_block = idct2d(dct_block)
            
            # Place in output
            reconstructed[i:i+block_size, j:j+block_size] = spatial_block
            
            block_idx += 1
    
    return reconstructed


def zigzag_order(block_size=8):
    """
    Generate zigzag scan order for block
    
    Returns:
        List of (row, col) tuples in zigzag order
    """
    zigzag = []
    for diag in range(2 * block_size - 1):
        if diag % 2 == 0:
            # Even diagonal: top-right to bottom-left
            for i in range(max(0, diag - block_size + 1), min(diag + 1, block_size)):
                j = diag - i
                zigzag.append((i, j))
        else:
            # Odd diagonal: bottom-left to top-right
            for i in range(min(diag, block_size - 1), max(-1, diag - block_size), -1):
                j = diag - i
                zigzag.append((i, j))
    
    return zigzag


def zigzag_flatten(block):
    """Flatten block in zigzag order"""
    order = zigzag_order(block.shape[0])
    return np.array([block[i, j] for i, j in order])


def zigzag_unflatten(flattened, block_size=8):
    """Reconstruct block from zigzag-ordered array"""
    block = np.zeros((block_size, block_size), dtype=flattened.dtype)
    order = zigzag_order(block_size)
    for idx, (i, j) in enumerate(order):
        block[i, j] = flattened[idx]
    return block
