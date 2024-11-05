import unittest
from main import upload_jsonl
import os


class TestUploadJsonl(unittest.TestCase):
    def test_upload_jsonl(self):
        # Create a dummy JSONL file for testing
        with open("test_tasks.jsonl", "w") as f:
            f.write('{"task_description": "Test task"}\n')
        response = upload_jsonl("test_tasks.jsonl")
        self.assertIn("id", response)
        os.remove("test_tasks.jsonl")


if __name__ == "__main__":
    unittest.main()
