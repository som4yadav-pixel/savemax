import unittest

from savemax.app.calculator import TaxInputs, calculate_old_regime, calculate_new_regime


class TestCalculator(unittest.TestCase):
	def test_basic(self):
		inputs = TaxInputs(annual_income=1000000, deduction_80c=150000, deduction_80d=25000, hra=0, other_deductions=0)
		old_res = calculate_old_regime(inputs)
		new_res = calculate_new_regime(inputs)
		self.assertGreaterEqual(old_res["tax"], 0)
		self.assertGreaterEqual(new_res["tax"], 0)
		self.assertGreaterEqual(old_res["taxable_income"], 0)
		self.assertGreaterEqual(new_res["taxable_income"], 0)


if __name__ == "__main__":
	unittest.main()