#!/usr/bin/env python3
"""
Convert Markdown report to PDF with Chinese support and LaTeX math rendering
Uses markdown2 + weasyprint for professional PDF output
"""

import markdown2
from pathlib import Path
import subprocess
import os
import re

def markdown_to_html(md_path):
    """Convert markdown to HTML with proper Chinese styling and math support"""
    
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML with extras
    html_body = markdown2.markdown(
        md_content,
        extras=['fenced-code-blocks', 'tables', 'cuddled-lists', 'header-ids']
    )
    
    # Create full HTML with styling and MathJax
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>醫學影像壓縮編碼系統 - 技術報告</title>
    <!-- MathJax for LaTeX math rendering -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        @page {{
            size: A4;
            margin: 2cm 1.5cm;
            @bottom-center {{
                content: counter(page) " / " counter(pages);
                font-size: 9pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: 'Noto Sans CJK TC', 'Noto Sans CJK SC', sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
            max-width: 900px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: #2c3e50;
            font-size: 24pt;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-before: auto;
        }}
        
        h2 {{
            color: #34495e;
            font-size: 18pt;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 8px;
            margin-top: 25px;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: #2c3e50;
            font-size: 14pt;
            margin-top: 20px;
            page-break-after: avoid;
        }}
        
        h4 {{
            color: #555;
            font-size: 12pt;
            margin-top: 15px;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            font-size: 10pt;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            color: #c7254e;
        }}
        
        pre {{
            background-color: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 9pt;
            line-height: 1.4;
            page-break-inside: avoid;
        }}
        
        pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}
        
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #bdc3c7;
            margin: 30px 0;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        .equation {{
            text-align: center;
            margin: 15px 0;
            font-style: italic;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""
    
    return html

def html_to_pdf_weasyprint(html_content, output_pdf):
    """Convert HTML to PDF using weasyprint"""
    from weasyprint import HTML, CSS
    
    # Create HTML object
    html_obj = HTML(string=html_content)
    
    # Generate PDF
    html_obj.write_pdf(output_pdf)
    print(f"✓ PDF generated: {output_pdf}")

def main():
    md_path = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.md')
    html_path = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.html')
    pdf_path = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.pdf')
    
    print("Converting Markdown → HTML → PDF...")
    
    # Step 1: MD → HTML
    print("  [1/2] Markdown → HTML")
    html_content = markdown_to_html(md_path)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"      ✓ {html_path}")
    
    # Step 2: HTML → PDF
    print("  [2/2] HTML → PDF")
    try:
        html_to_pdf_weasyprint(html_content, pdf_path)
    except ImportError:
        print("      ⚠ weasyprint not installed, trying alternative...")
        # Fallback: use wkhtmltopdf
        cmd = [
            'wkhtmltopdf',
            '--encoding', 'utf-8',
            '--enable-local-file-access',
            str(html_path),
            str(pdf_path)
        ]
        subprocess.run(cmd, check=True)
        print(f"      ✓ {pdf_path}")
    
    print(f"\n✓ PDF report ready: {pdf_path}")
    print(f"  Size: {pdf_path.stat().st_size / 1024:.1f} KB")

if __name__ == '__main__':
    main()
