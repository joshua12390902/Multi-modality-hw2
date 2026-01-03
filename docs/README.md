# Medical Image Codec

A lossy compression system for 16-bit medical images (CT/MR) implementing block DCT, quantization, and Huffman entropy coding.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Usage

**1. Generate test data:**
```bash
python generate_test_data.py
```

**2. Encode an image:**
```bash
python encode.py --input test_data/ct_512x512.dcm --output compressed.bin --quality 75
```

**3. Decode the image:**
```bash
python decode.py --input compressed.bin --output reconstructed.raw
```

**4. Run full evaluation:**
```bash
python evaluate.py --input test_data/ct_512x512.dcm --qualities 30 60 90 --output results/
```

## Features

✓ **16-bit Support**: Handles 12-16 bit medical images end-to-end  
✓ **High Compression**: Achieves 14-15× compression ratios  
✓ **Quality Control**: Adjustable quality parameter (1-100)  
✓ **Custom Bitstream**: Self-contained binary format with magic number and version  
✓ **Standard Metrics**: Computes RMSE, PSNR, bpp, compression ratio  
✓ **Visualizations**: Generates comparison images and rate-distortion plots  

## Architecture

### Encoder Pipeline
```
DICOM Input → Padding → 8×8 DCT → Quantization → Zigzag → Huffman → Bitstream
```

### Decoder Pipeline
```
Bitstream → Parse → Huffman Decode → Inverse Zigzag → Dequantize → IDCT → Output
```

## Results Summary

Example results on 512×512 16-bit CT image:

| Quality | Size (bytes) | Ratio | Bits/Pixel | PSNR (dB) |
|---------|--------------|-------|------------|-----------|
| Q=30    | 33,409       | 15.7:1| 1.020      | 49.31     |
| Q=60    | 33,798       | 15.5:1| 1.031      | 54.19     |
| Q=90    | 35,401       | 14.8:1| 1.080      | 57.21     |

## File Structure

```
MMIP_hw2/
├── encode.py                 # Encoder command-line tool
├── decode.py                 # Decoder command-line tool
├── evaluate.py               # Performance evaluation script
├── dct_transform.py          # DCT/IDCT and quantization
├── huffman_coding.py         # Huffman entropy coding
├── bitstream.py              # Binary bitstream format
├── utils.py                  # I/O and metrics utilities
├── generate_test_data.py     # Synthetic data generator
├── requirements.txt          # Python dependencies
├── REPORT.md                 # Technical report
├── README.md                 # This file
├── test_data/                # Test DICOM images
└── results/                  # Evaluation outputs
    ├── results.csv           # Metrics table
    ├── results.json          # Detailed results
    ├── rate_distortion.png   # R-D plot
    └── comparison_q*.png     # Visual comparisons
```

## Bitstream Format

| Field | Size | Description |
|-------|------|-------------|
| Magic | 4B | 'MEDC' |
| Version | 1B | 0x01 |
| Width, Height | 2B each | Image dimensions |
| Bit Depth | 1B | 12-16 |
| Block Size | 1B | 8 |
| Quality | 1B | 1-100 |
| Quant Matrix | Variable | uint16 array |
| Huffman Table | Variable | Serialized codes |
| Encoded Data | Variable | Compressed coefficients |

## Command-Line Reference

### encode.py
```
--input <path>       Input DICOM file (required)
--output <path>      Output compressed file (required)
--quality <1-100>    Quality parameter (default: 75)
--block-size <n>     DCT block size (default: 8)
```

### decode.py
```
--input <path>       Input compressed file (required)
--output <path>      Output raw image file (required)
```

### evaluate.py
```
--input <path>       Input DICOM file (required)
--qualities <list>   Quality levels to test (default: 25 50 75)
--output <dir>       Output directory (default: results)
```

## Technical Details

- **Transform**: 2D DCT (8×8 blocks) using scipy.fftpack
- **Quantization**: JPEG-style matrix scaled for 16-bit images
- **Entropy Coding**: Adaptive Huffman based on coefficient statistics
- **Coefficient Order**: Zigzag scan for better compression
- **Error Handling**: Validates bitstream magic number and version

## Requirements

- Python 3.7+
- numpy
- scipy
- pydicom
- matplotlib
- Pillow

## Testing

Run the evaluation pipeline:
```bash
python generate_test_data.py
python evaluate.py --input test_data/ct_512x512.dcm --qualities 30 60 90
```

Check results in `results/` directory.

## Limitations

- 2D only (no 3D/volumetric compression)
- Fixed 8×8 blocks
- No ROI (region of interest) support
- Basic quantization matrix (not optimized per modality)

## Future Improvements

- ROI-aware encoding for diagnostic regions
- Progressive decoding support
- 3D/volumetric extension with inter-slice prediction
- Perceptual quantization matrices
- Error resilience mechanisms

## License

Educational project for Multi-Modal Image Processing course.

## Author

Multi-Modal Image Processing - Homework 2  
January 2026
