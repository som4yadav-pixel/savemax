from __future__ import annotations

import os
from pathlib import Path
from typing import Dict
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
import plotly.graph_objects as go

from savemax.app.auth import is_authenticated, login, logout, signup, SESSION_USER_KEY
from savemax.app.calculator import TaxInputs, calculate_old_regime, calculate_new_regime
from savemax.app.database import ensure_dbs, save_history, get_recent_history
from savemax.app.recommender import compare_regimes, generate_suggestions
from savemax.app.ui_components import gradient_header, metric_card, two_column_metrics, format_inr
from savemax.app.exports import export_csv, export_pdf

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS for API routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "savemax_logo.png"
CUSTOM_CSS = ASSETS_DIR / "custom.css"


def _ensure_logo():
	ASSETS_DIR.mkdir(parents=True, exist_ok=True)
	if not LOGO_PATH.exists():
		# Generate a minimal placeholder PNG (1x1 transparent) if logo missing
		try:
			from PIL import Image
			img = Image.new("RGBA", (512, 512), (37, 117, 252, 255))
			img.save(LOGO_PATH)
		except Exception:
			# Fallback to write a tiny PNG header to avoid errors
			with open(LOGO_PATH, "wb") as f:
				f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x04\x00\x01\x0b\x0e\x1d\xb7\x00\x00\x00\x00IEND\xaeB`\x82")


def _inject_css():
	if CUSTOM_CSS.exists():
		st.markdown(f"<style>{CUSTOM_CSS.read_text()}</style>", unsafe_allow_html=True)


def _login_signup_ui() -> None:
	st.title("SaveMax – Login")
	col1, col2 = st.columns(2)
	with col1:
		st.subheader("Login")
		username = st.text_input("Username", key="login_user")
		password = st.text_input("Password", type="password", key="login_pass")
		if st.button("🔑 Login"):
			if login(username, password):
				st.success("Welcome back!")
				st.rerun()
			else:
				st.error("Invalid credentials")
	with col2:
		st.subheader("Sign Up")
		su_user = st.text_input("New Username", key="su_user")
		su_pass = st.text_input("New Password", type="password", key="su_pass")
		if st.button("🆕 Create Account"):
			if signup(su_user, su_pass):
				st.success("Account created. You can log in now.")
			else:
				st.error("Username already exists. Choose another.")


def _dashboard_ui(username: str) -> None:
	gradient_header("SaveMax Dashboard", "Smarter Tax, Bigger Savings", str(LOGO_PATH))

	with st.sidebar:
		st.header("Inputs")
		income = st.slider("Annual Income", 0, 20000000, 700000, step=10000)
		st.markdown("### Deductions (Old Regime)")
		d80c = st.number_input("80C (Investments)", min_value=0, max_value=2000000, value=0, step=5000)
		d80d = st.number_input("80D (Medical Insurance)", min_value=0, max_value=2000000, value=0, step=1000)
		hra = st.number_input("HRA", min_value=0, max_value=2000000, value=0, step=1000)
		other = st.number_input("Others", min_value=0, max_value=2000000, value=0, step=1000)
		regime_choice = st.selectbox("Regime", ["Auto Compare", "Old Regime", "New Regime"], index=0)
		st.divider()
		if st.button("🚪 Logout"):
			logout()
			st.rerun()

	inputs = TaxInputs(
		annual_income=income,
		deduction_80c=d80c,
		deduction_80d=d80d,
		hra=hra,
		other_deductions=other,
	)

	preferred, old_res, new_res = compare_regimes(inputs)

	st.markdown("### Summary")
	metrics: Dict[str, str] = {
		"Gross Income": format_inr(old_res["gross_income"]),
		"Total Deductions": format_inr(old_res["total_deductions"]),
		"Taxable Income (Old)": format_inr(old_res["taxable_income"]),
		"Taxable Income (New)": format_inr(new_res["taxable_income"]),
		"Tax Payable (Old)": format_inr(old_res["tax"]),
		"Tax Payable (New)": format_inr(new_res["tax"]),
	}
	two_column_metrics(metrics)

	if regime_choice == "Auto Compare":
		cheaper = "Old Regime" if old_res["tax"] < new_res["tax"] else "New Regime"
		delta = abs(old_res["tax"] - new_res["tax"])
		st.success(f"💡 Save with SaveMax: {cheaper} saves ₹{delta:,.0f} compared to the other.")
		_to_plot = {
			"Old Regime": old_res["tax"],
			"New Regime": new_res["tax"],
		}
		fig = go.Figure(data=[go.Bar(x=list(_to_plot.keys()), y=list(_to_plot.values()), marker_color=["#6a11cb", "#2575fc"])])
		fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
		st.plotly_chart(fig, use_container_width=True)
		chosen_regime = cheaper
	elif regime_choice == "Old Regime":
		chosen_regime = "Old Regime"
		st.info("Showing Old Regime results.")
	else:
		chosen_regime = "New Regime"
		st.info("Showing New Regime results.")

	# Save to history
	if st.button("💾 Save Calculation"):
		res = old_res if chosen_regime == "Old Regime" else new_res
		save_history(username, chosen_regime, inputs.annual_income, inputs.total_deductions_old, res["tax"])
		st.success("Saved to history.")

	tab1, tab2, tab3 = st.tabs(["History", "Export", "Suggestions"])
	with tab1:
		recs = get_recent_history(username)
		if recs:
			df = pd.DataFrame(recs, columns=["date", "regime", "income", "tax"]) \
				.assign(income=lambda d: d["income"].map(lambda v: f"₹{v:,.0f}")) \
				.assign(tax=lambda d: d["tax"].map(lambda v: f"₹{v:,.0f}"))
			st.dataframe(df, use_container_width=True, hide_index=True)
			# Line chart (numeric)
			df_num = pd.DataFrame(recs, columns=["date", "regime", "income", "tax"]).sort_values("date")
			df_num["date"] = pd.to_datetime(df_num["date"]) 
			df_num = df_num.set_index("date")["tax"]
			st.line_chart(df_num)
		else:
			st.caption("No history yet. Save a calculation to see it here.")

	with tab2:
		rows = [
			{"Metric": "Gross Income", "Old": old_res["gross_income"], "New": new_res["gross_income"]},
			{"Metric": "Taxable Income", "Old": old_res["taxable_income"], "New": new_res["taxable_income"]},
			{"Metric": "Tax Payable", "Old": old_res["tax"], "New": new_res["tax"]},
		]
		csv_bytes = export_csv(rows)
		st.download_button("⬇️ Export CSV", csv_bytes, file_name="savemax_report.csv", mime="text/csv")

		summary = {
			"Preferred Regime": chosen_regime,
			"Gross Income": f"₹{inputs.annual_income:,.0f}",
			"Total Deductions (Old)": f"₹{inputs.total_deductions_old:,.0f}",
			"Tax Old": f"₹{old_res['tax']:,.0f}",
			"Tax New": f"₹{new_res['tax']:,.0f}",
		}
		pdf_bytes = export_pdf(summary, rows)
		st.download_button("🧾 Export PDF", pdf_bytes, file_name="savemax_report.pdf", mime="application/pdf")

	with tab3:
		suggestions = generate_suggestions(inputs, old_res["tax"], new_res["tax"])
		for s in suggestions:
			st.write("• ", s)


def main() -> None:
	st.set_page_config(page_title="SaveMax", page_icon="💸", layout="wide")
	ensure_dbs()
	_ensure_logo()
	_inject_css()

	if not is_authenticated():
		_login_signup_ui()
		return

	username = st.session_state[SESSION_USER_KEY]
	_dashboard_ui(username)


if __name__ == "__main__":
	ensure_dbs()
	_ensure_logo()
	app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 