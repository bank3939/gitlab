import unittest

from app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_index(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("mode", r.get_data(as_text=True))

    def test_a1_divider(self):
        r = self.client.post("/", data={
            "mode": "divider", "VCC": "12", "RC": "2200", "beta": "100", "VBE": "0.7",
            "R1": "100000", "R2": "22000", "RE": "1000"
        })
        text = r.get_data(as_text=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn("1.22986", text)
        self.assertIn("8.0521", text)

    def test_a5_invalid_input(self):
        r = self.client.post("/", data={
            "mode": "fixed", "VCC": "12", "RC": "2200", "beta": "100", "VBE": "0.7", "RB": "0"
        })
        text = r.get_data(as_text=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue("ข้อผิดพลาด" in text or "RB" in text)
        self.assertNotIn("ผลลัพธ์ DC Operating Point", text)  # no computed result for this invalid request

    def test_unknown_mode(self):
        r = self.client.post("/", data={"mode": "bogus", "VCC": "12", "RC": "2200", "beta": "100", "VBE": "0.7"})
        self.assertIn("ไม่รู้จักโหมด", r.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
