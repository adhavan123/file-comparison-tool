import io

import pandas as pd


def export_csv(diff_df: pd.DataFrame) -> bytes:
    """Return the difference table as CSV bytes."""
    return diff_df.to_csv(index=False).encode("utf-8")


def export_excel(diff_df: pd.DataFrame) -> bytes:
    """Return the difference table as an .xlsx file, in bytes."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        diff_df.to_excel(writer, index=False, sheet_name="Differences")
    return buffer.getvalue()


def export_pdf(result: dict) -> bytes:
    """Return a PDF summary report (metrics + difference table), in bytes."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("File Comparison Report", styles["Title"]))
    elements.append(Spacer(1, 0.5 * cm))

    summary_rows = [
        ["Metric", "Value"],
        ["Total Rows", result.get("totalRows", 0)],
        ["Matched Rows", result.get("matchedRows", 0)],
        ["Modified Rows", result.get("modifiedRows", 0)],
        ["Added Rows", result.get("addedRows", 0)],
        ["Removed Rows", result.get("removedRows", 0)],
        ["Match %", f"{result.get('matchPercentage', 0)}%"],
    ]

    summary_table = Table(summary_rows, hAlign="LEFT")
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#292A2E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DAD5C8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F7F5F0")]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 1 * cm))

    differences = result.get("differences", [])

    if differences:
        elements.append(Paragraph("Differences", styles["Heading2"]))
        elements.append(Spacer(1, 0.3 * cm))

        headers = list(differences[0].keys())
        table_data = [headers] + [
            [str(row.get(h, "")) for h in headers] for row in differences
        ]

        diff_table = Table(table_data, repeatRows=1, hAlign="LEFT")
        diff_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222326")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EEEAE1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F3EFE5")]),
        ]))
        elements.append(diff_table)
    else:
        elements.append(Paragraph("No differences found.", styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()