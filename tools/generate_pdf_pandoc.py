#!/usr/bin/env python3
"""
Convert FINAL_REPORT.md to PDF using pandoc with LaTeX math support
"""

import subprocess
import os
from pathlib import Path

def generate_pdf_with_pandoc():
    """Use pandoc to convert markdown to PDF with proper LaTeX rendering"""
    
    md_file = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.md')
    pdf_file = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.pdf')
    
    # Check if pandoc is available
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("✗ pandoc not found. Please install it first:")
        print("  apt-get install pandoc texlive-xetex texlive-fonts-recommended texlive-latex-extra")
        return False
    
    # Pandoc command with options for Chinese and LaTeX math
    cmd = [
        'pandoc',
        str(md_file),
        '-o', str(pdf_file),
        '--pdf-engine=xelatex',  # Use xelatex for CJK support
        '--variable=CJKmainfont:SimSun',  # Fallback CJK font (may need adjustment)
        '--table-of-contents',  # Add table of contents
        '--number-sections',  # Number sections
        '-V', 'fontsize=11pt',
        '-V', 'documentclass=article',
        '-V', 'geometry:margin=2cm',
        '--from=markdown',
        '--to=pdf'
    ]
    
    print("Generating PDF with pandoc + xelatex...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            file_size = pdf_file.stat().st_size / 1024
            print(f"✓ PDF generated: {pdf_file}")
            print(f"  Size: {file_size:.1f} KB")
            return True
        else:
            print(f"✗ Pandoc error:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✗ PDF generation timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    if generate_pdf_with_pandoc():
        print("\n✓ Report ready for delivery")
    else:
        print("\n⚠ Falling back to previous PDF generation method")
        # Try to use the existing markdown2 method
        subprocess.run(['/usr/bin/python3', '/workspace/MMIP_hw2/tools/generate_pdf.py'])
