import unittest


class TestApp(unittest.TestCase):
    def setUp(self):
        import app

        self.client = app.app.test_client()
        self.client.testing = True

    def test_get_index_contains_vcc(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"VCC", resp.data)

    def test_post_computes_and_contains_vce(self):
        payload = {
            "VCC": "12",
            "R1": "40000",
            "R2": "10000",
            "RC": "2000",
            "RE": "1000",
            "beta": "100",
            "VBE": "0.7",
        }
        resp = self.client.post("/", data=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"VCE", resp.data)


if __name__ == "__main__":
    unittest.main()
