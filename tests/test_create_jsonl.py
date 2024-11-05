import unittest
import json
import os
from main import create_jsonl

class TestCreateJsonl(unittest.TestCase):

    def setUp(self):
        # Create a test image
        self.image_path = "jj_images/sample_image.jpg"
        if not os.path.exists("jj_images"):
            os.makedirs("jj_images")
        with open(self.image_path, "wb") as f:
            f.write(
                b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00..."
            )

    def test_create_jsonl(self):
        # Test JSONL creation
        image_files = [self.image_path]
        jsonl_path = create_jsonl(image_files)

        self.assertTrue(os.path.exists(jsonl_path))

        with open(jsonl_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                task = json.loads(line)
                self.assertIn("custom_id", task)
                self.assertEqual(task["custom_id"], f"task-{index}")
                self.assertIn("body", task)
                self.assertIn("model", task["body"])
                self.assertIn("messages", task["body"])
                self.assertIsInstance(task["body"]["messages"], list)
                self.assertGreater(len(task["body"]["messages"]), 0)
                # Check if the image URL is present in the task structure
                user_content = task["body"]["messages"][-1]["content"]
                self.assertIsInstance(user_content, list)
                self.assertEqual(user_content[0]["type"], "image_url")

        os.remove(jsonl_path)

    def tearDown(self):
        # Clean up by removing the test image
        if os.path.exists(self.image_path):
            os.remove(self.image_path)


if __name__ == "__main__":
    unittest.main()
