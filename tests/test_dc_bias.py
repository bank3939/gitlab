import unittest

from dc_bias import calculate_fixed_bias, calculate_emitter_bias, calculate_voltage_divider_bias


class TestDCBias(unittest.TestCase):
    def test_a1_divider(self):
        r = calculate_voltage_divider_bias(12, 2200, 100, 0.7, 100000, 22000, 1000)
        self.assertAlmostEqual(r["ic_ma"], 1.22986, places=4)
        self.assertAlmostEqual(r["vce_v"], 8.05216, places=4)
        self.assertEqual(r["errors"], [])
        self.assertEqual(r["warnings"], [])

    def test_a2_fixed(self):
        r = calculate_fixed_bias(12, 2200, 100, 0.7, 1_000_000)
        self.assertAlmostEqual(r["ic_ma"], 1.13, places=4)
        self.assertAlmostEqual(r["vce_v"], 9.514, places=3)
        self.assertAlmostEqual(r["ve_v"], 0.0, places=6)

    def test_a3_emitter(self):
        r = calculate_emitter_bias(12, 2200, 100, 0.7, 1_000_000, 1000)
        self.assertAlmostEqual(r["ic_ma"], 1.02634, places=4)
        self.assertAlmostEqual(r["vce_v"], 8.70545, places=4)

    def test_a4_emitter_re_increase(self):
        r = calculate_emitter_bias(12, 2200, 100, 0.7, 1_000_000, 2000)
        self.assertAlmostEqual(r["ic_ma"], 0.94010, places=4)
        self.assertAlmostEqual(r["vce_v"], 8.03278, places=4)

    def test_a5_invalid_rb(self):
        r = calculate_fixed_bias(12, 2200, 100, 0.7, 0)
        self.assertTrue(r["errors"])
        self.assertIsNone(r["ic_ma"])

    def test_divider_original_case_preserved(self):
        # matches earlier lab divider case
        r = calculate_voltage_divider_bias(12, 2000, 100, 0.7, 40000, 10000, 1000)
        self.assertAlmostEqual(r["vth_v"], 2.4, places=6)
        self.assertAlmostEqual(r["rth_ohm"], 8000.0, places=6)
        self.assertAlmostEqual(r["ic_ma"], 100 * 1.7 / 109000 * 1000, places=6)
        self.assertAlmostEqual(r["vce_v"], 12 - (100 * 1.7 / 109000) * 2000 - (101 * 1.7 / 109000) * 1000, places=6)


if __name__ == "__main__":
    unittest.main()
