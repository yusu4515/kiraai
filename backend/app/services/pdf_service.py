"""PDF generation service using WeasyPrint"""

import io
from weasyprint import HTML


BASE_CSS = """
@page {
    size: A4;
    margin: 15mm;
}
body {
    font-family: 'Noto Sans CJK JP', 'Noto Sans JP', sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #333;
}
table {
    border-collapse: collapse;
    width: 100%;
}
th, td {
    border: 1px solid #333;
    padding: 4px 8px;
    text-align: left;
    font-size: 9pt;
}
th {
    background-color: #f0f0f0;
    font-weight: bold;
}
h1 { font-size: 16pt; text-align: center; margin-bottom: 16px; }
h2 { font-size: 12pt; border-bottom: 2px solid #333; padding-bottom: 4px; margin-top: 16px; }
h3 { font-size: 11pt; margin-top: 12px; }
"""


def html_to_pdf(html_content: str) -> bytes:
    """Convert HTML content to PDF bytes

    Args:
        html_content: HTML string to convert

    Returns:
        PDF file as bytes
    """
    # Wrap with base CSS if not already a full HTML document
    if "<html" not in html_content.lower():
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <style>{BASE_CSS}</style>
        </head>
        <body>{html_content}</body>
        </html>
        """
    elif "<style" not in html_content.lower():
        # Inject base CSS into existing HTML
        html_content = html_content.replace("</head>", f"<style>{BASE_CSS}</style></head>")

    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.read()
