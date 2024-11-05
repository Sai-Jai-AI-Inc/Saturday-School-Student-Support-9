import unittest
from main import retrieve_batch_results


class TestRetrieveBatchResults(unittest.TestCase):
    def test_retrieve_batch_results(self):
        # Replace with an actual batch ID for testing
        response = retrieve_batch_results("test_batch_id")
        self.assertIsInstance(response, list)


if __name__ == "__main__":
    unittest.main()
