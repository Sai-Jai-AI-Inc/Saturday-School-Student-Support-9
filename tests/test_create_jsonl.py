import unittest
import os
from main import create_jsonl


class TestCreateJsonl(unittest.TestCase):
    def test_create_jsonl(self):
        image_files = ["jj_images/LINE_ALBUM_SSSS8 Wealth management_241104_2.jpg"]
        jsonl_path = create_jsonl(image_files)
        self.assertTrue(os.path.exists(jsonl_path))
        os.remove(jsonl_path)


if __name__ == "__main__":
    unittest.main()
