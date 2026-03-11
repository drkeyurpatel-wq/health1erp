"""PDF generation utilities for bills, discharge summaries, prescriptions, and lab reports."""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def generate_bill_pdf(bill_data: dict) -> bytes:
    """Generate a bill PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Health1ERP - Hospital Bill", styles["Title"]))
    elements.append(Spacer(1, 10 * mm))

    info = [
        ["Bill Number:", bill_data.get("bill_number", "")],
        ["Date:", str(bill_data.get("bill_date", ""))],
        ["Patient:", bill_data.get("patient_name", "")],
        ["UHID:", bill_data.get("uhid", "")],
    ]
    info_table = Table(info, colWidths=[120, 300])
    info_table.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 10)]))
    elements.append(info_table)
    elements.append(Spacer(1, 10 * mm))

    # Items table
    items_data = [["#", "Description", "Qty", "Rate", "Tax", "Total"]]
    for i, item in enumerate(bill_data.get("items", []), 1):
        items_data.append([
            str(i), item.get("description", ""),
            str(item.get("quantity", 1)), f"{item.get('unit_price', 0):.2f}",
            f"{item.get('tax_percent', 0)}%", f"{item.get('total', 0):.2f}",
        ])
    items_data.append(["", "", "", "", "Subtotal:", f"{bill_data.get('subtotal', 0):.2f}"])
    items_data.append(["", "", "", "", "Tax:", f"{bill_data.get('tax_amount', 0):.2f}"])
    items_data.append(["", "", "", "", "Discount:", f"-{bill_data.get('discount_amount', 0):.2f}"])
    items_data.append(["", "", "", "", "Total:", f"{bill_data.get('total_amount', 0):.2f}"])

    t = Table(items_data, colWidths=[30, 200, 40, 70, 50, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a56db")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -5), 0.5, colors.grey),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15 * mm))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()


def generate_discharge_summary_pdf(summary_data: dict) -> bytes:
    """Generate a discharge summary PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("DISCHARGE SUMMARY", styles["Title"]))
    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph(f"Patient: {summary_data.get('patient_name', '')}", styles["Heading3"]))
    elements.append(Paragraph(f"UHID: {summary_data.get('uhid', '')}", styles["Normal"]))
    elements.append(Paragraph(f"Admission: {summary_data.get('admission_date', '')}", styles["Normal"]))
    elements.append(Paragraph(f"Discharge: {summary_data.get('discharge_date', '')}", styles["Normal"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph("Diagnosis", styles["Heading3"]))
    elements.append(Paragraph(summary_data.get("diagnosis", "N/A"), styles["Normal"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph("Summary", styles["Heading3"]))
    elements.append(Paragraph(summary_data.get("summary_text", ""), styles["Normal"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph("Follow-up Instructions", styles["Heading3"]))
    elements.append(Paragraph(summary_data.get("follow_up", "As advised"), styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()


def generate_prescription_pdf(prescription_data: dict) -> bytes:
    """Generate a prescription PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("PRESCRIPTION", styles["Title"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph(f"Patient: {prescription_data.get('patient_name', '')}", styles["Normal"]))
    elements.append(Paragraph(f"Doctor: {prescription_data.get('doctor_name', '')}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {prescription_data.get('date', '')}", styles["Normal"]))
    elements.append(Spacer(1, 8 * mm))

    rx_header = [["Rx", "Medicine", "Dosage", "Frequency", "Duration"]]
    for i, item in enumerate(prescription_data.get("items", []), 1):
        rx_header.append([
            str(i), item.get("name", ""), item.get("dosage", ""),
            item.get("frequency", ""), item.get("duration", ""),
        ])

    t = Table(rx_header, colWidths=[30, 180, 80, 90, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d9488")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)

    doc.build(elements)
    return buffer.getvalue()


def generate_lab_report_pdf(report_data: dict) -> bytes:
    """Generate a lab report PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("LABORATORY REPORT", styles["Title"]))
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph(f"Patient: {report_data.get('patient_name', '')}", styles["Normal"]))
    elements.append(Paragraph(f"Order Date: {report_data.get('order_date', '')}", styles["Normal"]))
    elements.append(Spacer(1, 8 * mm))

    results_data = [["Test", "Result", "Unit", "Normal Range", "Flag"]]
    for r in report_data.get("results", []):
        flag = "H" if r.get("is_abnormal") else ""
        results_data.append([
            r.get("test_name", ""), r.get("result_value", ""),
            r.get("unit", ""), r.get("normal_range", ""), flag,
        ])

    t = Table(results_data, colWidths=[150, 80, 50, 120, 40])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)

    doc.build(elements)
    return buffer.getvalue()
