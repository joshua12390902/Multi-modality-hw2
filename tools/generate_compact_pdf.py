#!/usr/bin/env python3
"""
Generate compact PDF report (6-10 pages)
"""

import markdown2
from weasyprint import HTML
from pathlib import Path

def generate_compact_pdf():
    md_file = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT_COMPACT.md')
    pdf_file = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.pdf')
    html_file = Path('/workspace/MMIP_hw2/docs/FINAL_REPORT.html')
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    html_body = markdown2.markdown(
        md_content,
        extras=['fenced-code-blocks', 'tables', 'cuddled-lists', 'header-ids']
    )
    
    # Compact CSS for 6-10 pages
    css = """
    @page {
        size: A4;
        margin: 1.5cm 1.2cm;
    }
    
    body {
        font-family: 'Noto Sans CJK TC', 'Noto Sans CJK SC', sans-serif;
        font-size: 10pt;
        line-height: 1.4;
        color: #333;
    }
    
    h1 {
        font-size: 20pt;
        color: #2c3e50;
        border-bottom: 2.5pt solid #3498db;
        padding-bottom: 6pt;
        margin: 16pt 0 10pt 0;
        page-break-after: avoid;
    }
    
    h2 {
        font-size: 15pt;
        color: #34495e;
        border-bottom: 1.5pt solid #bdc3c7;
        padding-bottom: 4pt;
        margin: 14pt 0 8pt 0;
        page-break-after: avoid;
    }
    
    h3 {
        font-size: 12pt;
        color: #555;
        margin: 10pt 0 6pt 0;
        page-break-after: avoid;
    }
    
    h4 {
        font-size: 11pt;
        color: #666;
        margin: 8pt 0 4pt 0;
    }
    
    p {
        margin: 4pt 0;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 8pt 0;
        font-size: 9pt;
        page-break-inside: avoid;
    }
    
    th, td {
        border: 0.5pt solid #ddd;
        padding: 4pt 6pt;
        text-align: left;
    }
    
    th {
        background-color: #3498db;
        color: white;
        font-weight: bold;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    code {
        background-color: #f4f4f4;
        padding: 1pt 3pt;
        font-family: 'Courier New', monospace;
        font-size: 8.5pt;
        color: #c7254e;
    }
    
    pre {
        background-color: #f8f8f8;
        border: 0.5pt solid #ddd;
        padding: 6pt;
        font-size: 8pt;
        line-height: 1.3;
        page-break-inside: avoid;
        margin: 6pt 0;
    }
    
    pre code {
        background: none;
        padding: 0;
        color: #333;
    }
    
    ul, ol {
        margin: 4pt 0;
        padding-left: 18pt;
    }
    
    li {
        margin: 2pt 0;
    }
    
    hr {
        border: none;
        border-top: 1.5pt solid #bdc3c7;
        margin: 12pt 0;
    }
    
    strong {
        font-weight: 600;
        color: #2c3e50;
    }
    """
    
    # Full HTML
    full_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>醫學影像壓縮編碼系統 - 技術報告</title>
    <style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    # Save HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    # Generate PDF
    HTML(string=full_html).write_pdf(pdf_file)
    
    print(f"✓ 精簡版 PDF 已生成: {pdf_file}")
    
    # Check page count
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_file)
        page_count = len(reader.pages)
        size_kb = pdf_file.stat().st_size / 1024
        
        print(f"  頁數: {page_count} 頁")
        print(f"  大小: {size_kb:.1f} KB")
        
        if 6 <= page_count <= 10:
            print(f"  ✓ 符合6-10頁要求")
        else:
            print(f"  ⚠ 超出6-10頁範圍，需要調整")
    except:
        pass
    
    return pdf_file

if __name__ == '__main__':
    generate_compact_pdf()
