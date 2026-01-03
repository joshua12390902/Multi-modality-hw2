"""
Huffman entropy coding for DCT coefficients
"""
import numpy as np
from collections import Counter, defaultdict
import heapq


class HuffmanNode:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(symbols_freq):
    """
    Build Huffman tree from symbol frequencies
    
    Args:
        symbols_freq: Dict of {symbol: frequency}
        
    Returns:
        Root node of Huffman tree
    """
    if not symbols_freq:
        return None
    
    # Create leaf nodes
    heap = [HuffmanNode(symbol=sym, freq=freq) for sym, freq in symbols_freq.items()]
    heapq.heapify(heap)
    
    # Build tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        parent = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, parent)
    
    return heap[0]


def generate_huffman_codes(root):
    """
    Generate Huffman codes from tree
    
    Args:
        root: Root of Huffman tree
        
    Returns:
        Dict of {symbol: code_string}
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, code=''):
        if node.symbol is not None:  # Leaf node
            codes[node.symbol] = code if code else '0'
        else:
            if node.left:
                traverse(node.left, code + '0')
            if node.right:
                traverse(node.right, code + '1')
    
    traverse(root)
    return codes


def encode_huffman(data, codes):
    """
    Encode data using Huffman codes
    
    Args:
        data: List/array of symbols
        codes: Dict of {symbol: code_string}
        
    Returns:
        Encoded bitstring
    """
    return ''.join(codes[symbol] for symbol in data)


def decode_huffman(bitstring, root):
    """
    Decode bitstring using Huffman tree
    
    Args:
        bitstring: String of '0' and '1'
        root: Root of Huffman tree
        
    Returns:
        List of decoded symbols
    """
    if root is None or root.symbol is not None:
        # Single symbol tree
        return [root.symbol] * len(bitstring) if root else []
    
    symbols = []
    current = root
    
    for bit in bitstring:
        if bit == '0':
            current = current.left
        else:
            current = current.right
        
        if current.symbol is not None:  # Reached leaf
            symbols.append(current.symbol)
            current = root
    
    return symbols


def serialize_huffman_table(codes):
    """
    Serialize Huffman codes to bytes
    
    Format: num_symbols (2 bytes) + for each symbol: 
            symbol (2 bytes signed) + code_length (1 byte) + code (variable)
    
    Args:
        codes: Dict of {symbol: code_string}
        
    Returns:
        bytes
    """
    data = bytearray()
    
    # Number of symbols
    data.extend(len(codes).to_bytes(2, byteorder='big'))
    
    for symbol, code in codes.items():
        # Symbol (2 bytes, signed int16)
        symbol_bytes = int(symbol).to_bytes(2, byteorder='big', signed=True)
        data.extend(symbol_bytes)
        
        # Code length
        data.append(len(code))
        
        # Code (pack bits into bytes)
        code_bytes = int(code, 2).to_bytes((len(code) + 7) // 8, byteorder='big')
        data.extend(code_bytes)
    
    return bytes(data)


def deserialize_huffman_table(data):
    """
    Deserialize Huffman codes from bytes
    
    Args:
        data: bytes
        
    Returns:
        codes dict, bytes_read
    """
    codes = {}
    offset = 0
    
    # Number of symbols
    num_symbols = int.from_bytes(data[offset:offset+2], byteorder='big')
    offset += 2
    
    for _ in range(num_symbols):
        # Symbol
        symbol = int.from_bytes(data[offset:offset+2], byteorder='big', signed=True)
        offset += 2
        
        # Code length
        code_length = data[offset]
        offset += 1
        
        # Code
        num_bytes = (code_length + 7) // 8
        code_int = int.from_bytes(data[offset:offset+num_bytes], byteorder='big')
        code = bin(code_int)[2:].zfill(code_length)
        offset += num_bytes
        
        codes[symbol] = code
    
    return codes, offset


def bitstring_to_bytes(bitstring):
    """
    Convert bitstring to bytes
    
    Args:
        bitstring: String of '0' and '1'
        
    Returns:
        bytes, padding_bits
    """
    # Add padding
    padding = (8 - len(bitstring) % 8) % 8
    bitstring += '0' * padding
    
    # Convert to bytes
    data = bytearray()
    for i in range(0, len(bitstring), 8):
        byte = int(bitstring[i:i+8], 2)
        data.append(byte)
    
    return bytes(data), padding


def bytes_to_bitstring(data, num_bits):
    """
    Convert bytes to bitstring
    
    Args:
        data: bytes
        num_bits: Number of bits to extract
        
    Returns:
        Bitstring
    """
    bitstring = ''.join(format(byte, '08b') for byte in data)
    return bitstring[:num_bits]


def encode_coefficients(coeffs_list):
    """
    Encode list of coefficient arrays using Huffman coding
    
    Args:
        coeffs_list: List of coefficient arrays
        
    Returns:
        encoded_data (bytes), huffman_table (bytes), num_bits
    """
    # Flatten all coefficients
    all_coeffs = []
    for coeffs in coeffs_list:
        all_coeffs.extend(coeffs.flatten().tolist())
    
    # Build frequency table
    freq = Counter(all_coeffs)
    
    # Build Huffman tree and codes
    tree = build_huffman_tree(freq)
    codes = generate_huffman_codes(tree)
    
    # Encode
    bitstring = encode_huffman(all_coeffs, codes)
    num_bits = len(bitstring)
    
    # Convert to bytes
    encoded_bytes, padding = bitstring_to_bytes(bitstring)
    
    # Serialize Huffman table
    huffman_table = serialize_huffman_table(codes)
    
    return encoded_bytes, huffman_table, num_bits


def decode_coefficients(encoded_data, huffman_table, num_bits, num_coeffs):
    """
    Decode coefficients from Huffman-encoded data
    
    Args:
        encoded_data: bytes
        huffman_table: bytes (serialized Huffman table)
        num_bits: Number of bits in encoded data
        num_coeffs: Total number of coefficients to decode
        
    Returns:
        List of coefficients
    """
    # Deserialize Huffman table
    codes, _ = deserialize_huffman_table(huffman_table)
    
    # Rebuild tree from codes
    root = HuffmanNode()
    for symbol, code in codes.items():
        node = root
        for bit in code[:-1]:
            if bit == '0':
                if node.left is None:
                    node.left = HuffmanNode()
                node = node.left
            else:
                if node.right is None:
                    node.right = HuffmanNode()
                node = node.right
        
        # Last bit
        if code[-1] == '0':
            node.left = HuffmanNode(symbol=symbol, freq=0)
        else:
            node.right = HuffmanNode(symbol=symbol, freq=0)
    
    # Convert bytes to bitstring
    bitstring = bytes_to_bitstring(encoded_data, num_bits)
    
    # Decode
    coeffs = decode_huffman(bitstring, root)
    
    return coeffs[:num_coeffs]  # Trim to exact count
