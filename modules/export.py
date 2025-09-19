
import io
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Orders") -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def to_pdf_bytes(df: pd.DataFrame, company: str = "Agriculture & Forestry") -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 40, f"{company} - Warehouse Orders Export")
    c.setFont("Helvetica", 9)
    y = height - 70
    # Draw table (simple)
    cols = list(df.columns)
    col_width = (width - 80) / len(cols)
    # Header row
    for i, col in enumerate(cols):
        c.drawString(40 + i*col_width, y, str(col))
    y -= 14
    c.line(40, y+4, width-40, y+4)
    # Data rows (limit to fit)
    max_rows = int((y - 40) / 12)
    for r in df.head(max_rows).itertuples(index=False):
        for i, v in enumerate(r):
            s = str(v)
            if len(s) > 20:
                s = s[:17] + "..."
            c.drawString(40 + i*col_width, y, s)
        y -= 12
        if y < 40:
            c.showPage()
            y = height - 70
    c.save()
    return buffer.getvalue()
