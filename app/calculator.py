from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

STANDARD_DEDUCTION_NEW = 50000  # FY24-25
CESS_RATE = 0.04


@dataclass
class TaxInputs:
	annual_income: float
	deduction_80c: float = 0.0
	deduction_80d: float = 0.0
	hra: float = 0.0
	other_deductions: float = 0.0

	@property
	def total_deductions_old(self) -> float:
		return max(0.0, self.deduction_80c + self.deduction_80d + self.hra + self.other_deductions)

	@property
	def taxable_income_old(self) -> float:
		return max(0.0, self.annual_income - self.total_deductions_old)

	@property
	def taxable_income_new(self) -> float:
		return max(0.0, self.annual_income - STANDARD_DEDUCTION_NEW)


def _apply_slab_old(taxable: float) -> float:
	# Simplified Old Regime slabs (FY24-25, excluding surcharge thresholds)
	tax = 0.0
	remaining = taxable
	# 0 - 2.5L: 0%
	# 2.5 - 5L: 5%
	if remaining > 250000:
		chunk = min(remaining - 250000, 250000)
		tax += chunk * 0.05
	# 5 - 10L: 20%
	if remaining > 500000:
		chunk = min(remaining - 500000, 500000)
		tax += chunk * 0.20
	# 10L+: 30%
	if remaining > 1000000:
		chunk = remaining - 1000000
		tax += chunk * 0.30
	return tax


def _apply_slab_new(taxable: float) -> float:
	# New Regime slabs (FY24-25): 0 up to 3L, then 5%, 10%, 15%, 20%, 25% per 3L slab until 15L, then 30%
	tax = 0.0
	thresholds = [300000, 600000, 900000, 1200000, 1500000]
	rates = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25]
	prev = 0.0
	for idx, thr in enumerate(thresholds):
		if taxable > thr:
			if idx == 0:
				prev = thr
				continue
			chunk = thr - prev
			tax += chunk * rates[idx]
			prev = thr
		else:
			if taxable > prev:
				tax += (taxable - prev) * rates[idx]
			return tax
	# Above 15L: 30%
	if taxable > thresholds[-1]:
		tax += (taxable - thresholds[-1]) * 0.30
	return tax


def calculate_old_regime(inputs: TaxInputs) -> Dict[str, float]:
	taxable = inputs.taxable_income_old
	basic_tax = _apply_slab_old(taxable)
	cess = basic_tax * CESS_RATE
	total_tax = basic_tax + cess
	return {
		"gross_income": inputs.annual_income,
		"total_deductions": inputs.total_deductions_old,
		"taxable_income": taxable,
		"tax": total_tax,
		"cess": cess,
		"basic_tax": basic_tax,
	}


def calculate_new_regime(inputs: TaxInputs) -> Dict[str, float]:
	taxable = inputs.taxable_income_new
	basic_tax = _apply_slab_new(taxable)
	cess = basic_tax * CESS_RATE
	total_tax = basic_tax + cess
	return {
		"gross_income": inputs.annual_income,
		"total_deductions": STANDARD_DEDUCTION_NEW,
		"taxable_income": taxable,
		"tax": total_tax,
		"cess": cess,
		"basic_tax": basic_tax,
	} 