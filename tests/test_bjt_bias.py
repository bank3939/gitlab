import math
import unittest

from bjt_bias import analyze_bjt_ce


class TestBJTBias(unittest.TestCase):
    def test_active_reference(self):
        # Independent hand calculation:
        # VTH=12*10/(40+10)=2.4V, RTH=40k||10k=8000ohm
        # IB=(2.4-0.7)/(8000+101000)=1.7/109000 A
        # IC=100*IB, IE=101*IB
        # VCE=12 - IC*2000 - IE*1000, region "active", no errors.
        result = analyze_bjt_ce(
            VCC=12,
            R1=40000,
            R2=10000,
            RC=2000,
            RE=1000,
            beta=100,
            VBE=0.7,
        )
        vth = 12 * 10 / (40 + 10)
        rth = (40000 * 10000) / (40000 + 10000)
        ib = (2.4 - 0.7) / (8000 + 101000)
        ic = 100 * ib
        ie = 101 * ib
        vb = vth - ib * rth
        ve = ie * 1000
        vc = 12 - ic * 2000
        vce = 12 - ic * 2000 - ie * 1000

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["region"], "active")
        self.assertAlmostEqual(result["VTH"], vth, places=12)
        self.assertAlmostEqual(result["RTH"], rth, places=12)
        self.assertAlmostEqual(result["IB"], ib, places=15)
        self.assertAlmostEqual(result["IC"], ic, places=15)
        self.assertAlmostEqual(result["IE"], ie, places=15)
        self.assertAlmostEqual(result["VB"], vb, places=12)
        self.assertAlmostEqual(result["VE"], ve, places=12)
        self.assertAlmostEqual(result["VC"], vc, places=12)
        self.assertAlmostEqual(result["VCE"], vce, places=12)

    def test_saturation_warning(self):
        # VCC=5,R1=10000,R2=10000,RC=10000,RE=100,beta=200,VBE=0.7 => region "saturation", warnings contain "saturation".
        result = analyze_bjt_ce(
            VCC=5,
            R1=10000,
            R2=10000,
            RC=10000,
            RE=100,
            beta=200,
            VBE=0.7,
        )
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["region"], "saturation")
        self.assertTrue(
            any("saturation" in w.lower() for w in result["warnings"]),
            msg=f"warnings={result['warnings']}",
        )

    def test_cutoff(self):
        # VCC=12,R1=100000,R2=1000,RC=2000,RE=1000,beta=100,VBE=0.7 => region "cutoff", warnings present.
        result = analyze_bjt_ce(
            VCC=12,
            R1=100000,
            R2=1000,
            RC=2000,
            RE=1000,
            beta=100,
            VBE=0.7,
        )
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["region"], "cutoff")
        self.assertTrue(result["warnings"], msg="expected warnings present")

    def test_invalid_r1_zero(self):
        result = analyze_bjt_ce(
            VCC=12,
            R1=0,
            R2=10000,
            RC=2000,
            RE=1000,
            beta=100,
            VBE=0.7,
        )
        self.assertTrue(result["errors"], msg="expected errors present")


if __name__ == "__main__":
    unittest.main()
