from __future__ import annotations

import streamlit as st
from typing import Dict, Any

RUPEE = "₹"


def format_inr(amount: float) -> str:
	"""Format number as Indian Rupees with grouping.
	Example: 1234567.89 -> ₹12,34,567.89
	"""
	try:
		integer_part, _, fractional_part = f"{amount:,.2f}".partition(".")
		# Convert 1,234,567 to 12,34,567 (Indian grouping)
		parts = integer_part.split(",")
		if len(parts) <= 3:
			indian_grouped = integer_part
		else:
			head = parts[0]
			tail = "".join(parts[1:])
			first = tail[:-6]
			last6 = tail[-6:]
			grp = []
			while len(first) > 0:
				grp.append(first[-2:])
				first = first[:-2]
			indian_grouped = head + "," + ",".join(reversed(grp)) + "," + last6[:3] + "," + last6[3:]
		return f"{RUPEE}{indian_grouped}.{fractional_part}"
	except Exception:
		return f"{RUPEE}{amount:,.2f}"


def gradient_header(title: str, subtitle: str | None = None, logo_path: str | None = None) -> None:
	"""Renders a gradient header bar with optional logo."""
	st.markdown(
		"""
		<div class="gradient-header">
			{logo}
			<div>
				<div style="font-weight:800;font-size:1.1rem;letter-spacing:.2px;">{title}</div>
				{subtitle}
			</div>
		</div>
		""".format(
			logo=(f'<img src="{logo_path}" alt="logo" />' if logo_path else ""),
			title=title,
			subtitle=(f'<div style="opacity:.85;font-size:.85rem;">{subtitle}</div>' if subtitle else ""),
		),
		unsafe_allow_html=True,
	)


def metric_card(title: str, value: str) -> None:
	container = st.container()
	with container:
		st.markdown("<div class='neumorphic-card'>" f"<div class='title'>{title}</div>" f"<div class='value'>{value}</div>" "</div>", unsafe_allow_html=True)


def two_column_metrics(metrics: Dict[str, Any]) -> None:
	cols = st.columns(2)
	items = list(metrics.items())
	for idx, (title, value) in enumerate(items):
		with cols[idx % 2]:
			metric_card(title, value) 