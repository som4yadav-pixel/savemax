from __future__ import annotations

from io import BytesIO
from typing import List, Dict

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def export_csv(rows: List[Dict]) -> bytes:
	df = pd.DataFrame(rows)
	return df.to_csv(index=False).encode("utf-8")


def export_pdf(summary: Dict[str, str], comparison_rows: List[Dict[str, str]]) -> bytes:
	buffer = BytesIO()
	c = canvas.Canvas(buffer, pagesize=A4)
	width, height = A4
	margin = 20 * mm
	y = height - margin

	c.setFont("Helvetica-Bold", 16)
	c.drawString(margin, y, "SaveMax – Tax Summary Report")
	y -= 12 * mm

	c.setFont("Helvetica", 11)
	for key, value in summary.items():
		c.drawString(margin, y, f"{key}: {value}")
		y -= 7 * mm

	y -= 5 * mm
	c.setFont("Helvetica-Bold", 12)
	c.drawString(margin, y, "Old vs New Regime")
	y -= 8 * mm
	c.setFont("Helvetica", 10)

	for row in comparison_rows:
		line = ", ".join(f"{k}: {v}" for k, v in row.items())
		c.drawString(margin, y, line)
		y -= 6 * mm
		if y < margin + 20:
			c.showPage()
			y = height - margin

	c.showPage()
	c.save()
	buffer.seek(0)
	return buffer.read()