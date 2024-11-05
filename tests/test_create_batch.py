import unittest
from main import create_batch


class TestCreateBatch(unittest.TestCase):
    def test_create_batch(self):
        # Replace with an actual file ID for testing
        response = create_batch("test_file_id")
        self.assertIn("id", response)
        self.assertEqual(response["purpose"], "batch")


if __name__ == "__main__":
    unittest.main()
