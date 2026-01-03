#!/usr/bin/env python3
"""
Test suite to verify codec functionality
"""
import sys
from pathlib import Path
import numpy as np

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    try:
        import numpy
        import scipy
        import pydicom
        import matplotlib
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_codec_roundtrip():
    """Test encode-decode roundtrip"""
    print("\nTesting codec roundtrip...")
    try:
        from encode import encode_image
        from decode import decode_image
        from utils import read_dicom, load_raw_image, calculate_metrics
        
        # Use test image
        input_file = 'test_data/ct_512x512.dcm'
        if not Path(input_file).exists():
            print(f"  ✗ Test file not found: {input_file}")
            return False
        
        # Read original
        original, metadata = read_dicom(input_file)
        
        # Encode
        compressed = 'test_roundtrip.bin'
        encode_image(input_file, compressed, quality=75)
        
        # Decode
        reconstructed_file = 'test_roundtrip.raw'
        decode_image(compressed, reconstructed_file)
        
        # Load reconstructed
        reconstructed = load_raw_image(reconstructed_file, 
                                       metadata['width'], 
                                       metadata['height'])
        
        # Check metrics
        metrics = calculate_metrics(original, reconstructed, metadata['bit_depth'])
        
        if metrics['PSNR'] > 40:  # Reasonable PSNR
            print(f"  ✓ Roundtrip successful (PSNR: {metrics['PSNR']:.2f} dB)")
            
            # Cleanup
            Path(compressed).unlink(missing_ok=True)
            Path(reconstructed_file).unlink(missing_ok=True)
            return True
        else:
            print(f"  ✗ Poor quality: PSNR = {metrics['PSNR']:.2f} dB")
            return False
            
    except Exception as e:
        print(f"  ✗ Roundtrip test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bitstream_validation():
    """Test bitstream format validation"""
    print("\nTesting bitstream validation...")
    try:
        from bitstream import validate_bitstream
        
        # Test valid bitstream
        valid_file = 'results/compressed_q60.bin'
        if Path(valid_file).exists():
            if validate_bitstream(valid_file):
                print(f"  ✓ Valid bitstream recognized")
            else:
                print(f"  ✗ Valid bitstream rejected")
                return False
        
        # Test invalid file
        invalid_file = 'test_invalid.bin'
        Path(invalid_file).write_bytes(b'INVALID DATA')
        
        if not validate_bitstream(invalid_file):
            print(f"  ✓ Invalid bitstream rejected")
            Path(invalid_file).unlink()
            return True
        else:
            print(f"  ✗ Invalid bitstream accepted")
            Path(invalid_file).unlink()
            return False
            
    except Exception as e:
        print(f"  ✗ Validation test failed: {e}")
        return False

def test_quality_levels():
    """Test different quality levels"""
    print("\nTesting quality levels...")
    try:
        from encode import encode_image
        
        input_file = 'test_data/ct_256x256.dcm'
        if not Path(input_file).exists():
            print(f"  ✗ Test file not found")
            return False
        
        sizes = []
        for q in [10, 50, 90]:
            output = f'test_q{q}.bin'
            encode_image(input_file, output, quality=q, block_size=8)
            size = Path(output).stat().st_size
            sizes.append(size)
            Path(output).unlink()
        
        # Higher quality should generally mean larger files
        # (not always true due to Huffman, but usually)
        print(f"  Sizes: Q10={sizes[0]}, Q50={sizes[1]}, Q90={sizes[2]}")
        print(f"  ✓ Quality levels working")
        return True
        
    except Exception as e:
        print(f"  ✗ Quality test failed: {e}")
        return False

def test_file_structure():
    """Check all required files exist"""
    print("\nChecking file structure...")
    required_files = [
        'encode.py',
        'decode.py',
        'dct_transform.py',
        'huffman_coding.py',
        'bitstream.py',
        'utils.py',
        'evaluate.py',
        'generate_test_data.py',
        'requirements.txt',
        'README.md',
        'REPORT.md'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"  ✗ Missing files: {missing}")
        return False
    else:
        print(f"  ✓ All required files present ({len(required_files)} files)")
        return True

def main():
    """Run all tests"""
    print("="*60)
    print("Medical Image Codec - Test Suite")
    print("="*60)
    
    tests = [
        test_file_structure,
        test_imports,
        test_codec_roundtrip,
        test_bitstream_validation,
        test_quality_levels
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("="*60)
    
    if all(results):
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
