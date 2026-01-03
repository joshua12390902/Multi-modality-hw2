# Medical Image Codec

A lossy compression system for 16-bit medical images (CT/MR) implementing block DCT, quantization, and Huffman entropy coding.

## Quick Start

### Installation

```bash
cd /workspace/MMIP_hw2
pip install -r requirements.txt
```

### Usage - Codec

**1. Encode an image:**
```bash
python src/encode.py --input <dicom_file> --output compressed.bin --quality 60
```

**2. Decode the image:**
```bash
python src/decode.py --input compressed.bin --output reconstructed.raw
```

**3. Run full evaluation:**
```bash
python tools/evaluate_real_data.py
python tools/generate_visualizations.py
python tools/generate_compact_pdf.py
```

Results will be saved to `results_real/` and the report to `docs/FINAL_REPORT.pdf`.

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

Real evaluation on Medical Image Computing Platform (Medimodel) Human Skull CT data (5 slices, 512×512, 16-bit):

| Quality | PSNR (dB) | RMSE | Compression Ratio | Bits/Pixel | SSIM  | Edge PSNR (dB) |
|---------|-----------|------|-------------------|------------|-------|----------------|
| Q=30    | 48.54     | 3.86 | 15.62:1          | 1.022      | 0.9685| 23.58          |
| Q=60    | 50.96     | 2.87 | 15.41:1          | 1.031      | 0.9857| 24.64          |
| Q=90    | 53.21     | 2.19 | 15.21:1          | 1.049      | 0.9923| 25.31          |

**Key Findings:**
- Consistent 15-16× compression ratio across all quality levels
- Excellent structural preservation (SSIM > 0.96)
- Strong edge preservation verified by Edge PSNR metric
- RMSE variance < 2 dB across slices demonstrates robust codec

See [FINAL_REPORT.pdf](FINAL_REPORT.pdf) for detailed evaluation methodology and visualizations.

## File Structure

```
MMIP_hw2/
├── src/                      # Core codec implementation
│   ├── encode.py             # Encoder command-line tool
│   ├── decode.py             # Decoder command-line tool
│   ├── dct_transform.py      # DCT/IDCT and quantization matrices
│   ├── huffman_coding.py     # Huffman entropy coding
│   ├── bitstream.py          # Custom binary format
│   └── utils.py              # I/O and metrics utilities
├── tools/                    # Evaluation and visualization tools
│   ├── evaluate_real_data.py # Performance evaluation on real CT data
│   ├── generate_visualizations.py # Plots and comparisons
│   ├── generate_compact_pdf.py    # PDF report generation
│   └── export_metrics.py     # Metrics export to CSV/JSON
├── docs/
│   ├── FINAL_REPORT.pdf      # 10-page technical report with results
│   ├── FINAL_REPORT_COMPACT.md # Markdown source
│   └── README.md             # This file
├── results_real/             # Evaluation results on Medimodel CT data
│   ├── medimodel_results.json # Detailed metrics
│   ├── metrics_summary.csv   # Results table
│   ├── metrics_average.json  # Aggregate statistics
│   ├── performance_comparison.png
│   ├── rate_distortion_curve.png
│   ├── slice_details.png
│   └── qualitative_I150_Q60.png
├── requirements.txt          # Dependencies
└── README.md                 # Root README
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

Comprehensive evaluation was performed on real medical imaging data:

```bash
# Run evaluation on actual CT data
python tools/evaluate_real_data.py

# Generate performance visualizations
python tools/generate_visualizations.py

# Build final report
python tools/generate_compact_pdf.py
```

**Evaluation Dataset:** Medimodel Human Skull CT (5 consecutive slices)  
**Image Properties:** 512×512 pixels, 16-bit depth, JPEG Lossless DICOM  
**Results Location:** `results_real/` directory and `docs/FINAL_REPORT.pdf`

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

Student: 李朋逸 (Li Peng-Yi, 314831024)  
Course: Multi-Modal Image Processing - Homework 2  
Date: January 2026

**Repository:** https://github.com/user/medical-image-codec
