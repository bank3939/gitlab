import tempfile
import unittest
from pathlib import Path

import spice_engine


class TestSpiceEngine(unittest.TestCase):
    def test_validate_params_ok(self):
        p = spice_engine.validate_params({"VCC":12,"R1":100000,"R2":22000,"RC":2200,"RE":1000,"RL":10000,"Cin":10e-6,"Cout":10e-6,"amp_mV":10,"freq_hz":1000})
        self.assertEqual(p["VCC"], 12.0)
        self.assertAlmostEqual(p["Cin"], 10e-6)

    def test_validate_rejects_bad(self):
        with self.assertRaises(ValueError):
            spice_engine.validate_params({"R1":0})

    def test_build_netlist_contains_analysis(self):
        with tempfile.TemporaryDirectory() as wd:
            net, _ = spice_engine.build_netlist({"VCC":12,"R1":100000,"R2":22000,"RC":2200,"RE":1000,"RL":10000,"Cin":10e-6,"Cout":10e-6,"amp_mV":10,"freq_hz":1000}, "op", wd)
            self.assertIn("\nop\n", net)
            self.assertIn("Q2N3904", net)
            net, _ = spice_engine.build_netlist({"VCC":12,"R1":100000,"R2":22000,"RC":2200,"RE":1000,"RL":10000,"Cin":10e-6,"Cout":10e-6,"amp_mV":10,"freq_hz":1000}, "ac", wd)
            self.assertIn("ac dec", net)
            net, _ = spice_engine.build_netlist({"VCC":12,"R1":100000,"R2":22000,"RC":2200,"RE":1000,"RL":10000,"Cin":10e-6,"Cout":10e-6,"amp_mV":10,"freq_hz":1000}, "tran", wd)
            self.assertIn("\ntran ", net)

    def test_missing_ngspice_returns_error(self):
        # simulate missing by temporarily monkeypatching find_ngspice if needed; just check behavior when not found
        old = spice_engine.find_ngspice
        spice_engine.find_ngspice = lambda: None
        try:
            r = spice_engine.run_simulation("op", {"VCC":12,"R1":100000,"R2":22000,"RC":2200,"RE":1000,"RL":10000,"Cin":10e-6,"Cout":10e-6,"amp_mV":10,"freq_hz":1000})
            self.assertFalse(r["ok"])
            self.assertIn("ngspice", r["error"].lower())
        finally:
            spice_engine.find_ngspice = old


if __name__ == "__main__":
    unittest.main()
