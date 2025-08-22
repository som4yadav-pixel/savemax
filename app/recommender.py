from __future__ import annotations

from typing import Dict, Tuple

from savemax.app.calculator import TaxInputs, calculate_old_regime, calculate_new_regime, STANDARD_DEDUCTION_NEW


def compare_regimes(inputs: TaxInputs) -> Tuple[str, Dict[str, float], Dict[str, float]]:
	old_res = calculate_old_regime(inputs)
	new_res = calculate_new_regime(inputs)
	preferred = "Old Regime" if old_res["tax"] < new_res["tax"] else "New Regime"
	return preferred, old_res, new_res


def generate_suggestions(inputs: TaxInputs, old_tax: float, new_tax: float) -> list[str]:
	suggestions: list[str] = []
	# Tip 1: Maximize 80C up to 1.5L in old regime
	max_80c = 150000
	if inputs.deduction_80c < max_80c:
		gap = max_80c - inputs.deduction_80c
		suggestions.append(f"Invest {gap:,.0f} more under 80C to maximize benefits in Old Regime.")
	# Tip 2: Consider regime based on deductions
	if inputs.total_deductions_old > STANDARD_DEDUCTION_NEW:
		suggestions.append("Consider Old Regime since your deductions exceed the New Regime standard deduction.")
	else:
		suggestions.append("Consider New Regime if you have limited deductions this year.")
	# Tip 3: HRA reminder
	if inputs.hra <= 0:
		suggestions.append("If you pay rent, compute HRA exemption to reduce taxable income under Old Regime.")
	# Tip 4: Medical insurance
	if inputs.deduction_80d <= 0:
		suggestions.append("Buy/renew medical insurance to claim 80D deduction and improve coverage.")
	# High-level saving statement
	save_delta = abs(old_tax - new_tax)
	if save_delta > 0:
		better = "Old" if old_tax < new_tax else "New"
		suggestions.insert(0, f"Save with SaveMax: {better} Regime saves ₹{save_delta:,.0f} compared to the other.")
	return suggestions 