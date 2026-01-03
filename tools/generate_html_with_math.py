#!/usr/bin/env python3
"""
Convert Markdown to PDF with MathJax support for LaTeX formulas
"""

import markdown2
from pathlib import Path
import re

def process_latex_to_mathjax(md_content):
    """Convert LaTeX math to MathJax-compatible format"""
    # Already in $$ format, just need to ensure proper escaping
    return md_content

def generate_pdf_with_math():
    md_file = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.md')
    html_file = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.html')
    pdf_file = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.pdf')
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_body = markdown2.markdown(
        md_content,
        extras=['fenced-code-blocks', 'tables', 'cuddled-lists', 'header-ids', 'break-on-newline']
    )
    
    # Create full HTML with MathJax CDN
    full_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>醫學影像壓縮編碼系統 - 技術報告</title>
    
    <!-- MathJax for LaTeX rendering -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']],
                processEscapes: true
            }}
        }};
    </script>
    
    <style>
        @page {{
            size: A4;
            margin: 2cm 1.5cm;
        }}
        
        body {{
            font-family: 'Noto Sans CJK TC', 'Noto Sans CJK SC', 'Microsoft JhengHei', sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            color: #2c3e50;
            font-size: 24pt;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-after: avoid;
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
            font-family: 'Courier New', 'Consolas', monospace;
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
        
        .mjx-math {{
            font-size: 1.1em;
        }}
        
        @media print {{
            body {{
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""
    
    # Save HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✓ HTML 已生成: {html_file}")
    print(f"  包含 MathJax 支援，數學公式將正確顯示")
    print(f"\n請在瀏覽器中開啟 {html_file}")
    print("  然後使用「列印」→「另存為 PDF」來生成最終 PDF")
    print(f"  或使用: google-chrome --headless --print-to-pdf={pdf_file} {html_file}")
    
    return html_file

if __name__ == '__main__':
    generate_pdf_with_math()
