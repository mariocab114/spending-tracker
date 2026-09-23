import io
import unittest

from api import app


class TestCategorizeAPI(unittest.TestCase):
    def setUp(self):
        # Flask's test client sends fake requests without starting a server
        self.client = app.test_client()

    def post_csv(self, csv_text):
        data = {"file": (io.BytesIO(csv_text.encode()), "test.csv")}
        return self.client.post(
            "/api/categorize", data=data, content_type="multipart/form-data"
        )

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    def test_categorizes_transactions(self):
        csv_text = (
            "date,description,amount\n"
            "2026-08-01,Starbucks Coffee,5.75\n"
            "2026-08-02,Uber Ride,18.50\n"
            "2026-08-03,Mystery Store,10.00\n"
        )
        response = self.post_csv(csv_text)
        self.assertEqual(response.status_code, 200)

        body = response.get_json()
        categories = [t["category"] for t in body["transactions"]]
        self.assertEqual(categories, ["Food & Dining", "Transportation", "Uncategorized"])
        self.assertEqual(body["total_spent"], 34.25)

    def test_missing_file_returns_400(self):
        response = self.client.post("/api/categorize")
        self.assertEqual(response.status_code, 400)

    def test_missing_columns_returns_400(self):
        response = self.post_csv("date,amount\n2026-08-01,5.00\n")
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()