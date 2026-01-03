#!/bin/bash
# Package submission files

echo "Creating submission package..."

# Create submission directory
mkdir -p submission

# Copy source files
cp encode.py decode.py submission/
cp dct_transform.py huffman_coding.py bitstream.py utils.py submission/
cp evaluate.py generate_test_data.py submission/
cp requirements.txt submission/
cp README.md REPORT.md submission/

# Copy results
cp -r results submission/

# Copy test data (just one example)
mkdir -p submission/test_data
cp test_data/ct_512x512.dcm submission/test_data/

# Create zip file
cd submission
zip -r ../MMIP_hw2_submission.zip * >/dev/null 2>&1
cd ..

echo "✓ Created MMIP_hw2_submission.zip"
ls -lh MMIP_hw2_submission.zip

echo ""
echo "Submission contents:"
unzip -l MMIP_hw2_submission.zip | head -20
