import unittest
from main import encode_image_base64
import os


class TestEncodeImageBase64(unittest.TestCase):
    def setUp(self):
        # Set up a sample image path for testing
        self.image_path = "jj_images/sample_image.jpg"
        # Create a sample image file for testing (if not already present)
        if not os.path.exists("jj_images"):
            os.makedirs("jj_images")
        if not os.path.exists(self.image_path):
            with open(self.image_path, "wb") as f:
                f.write(
                    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00..."
                )

    def test_encode_image_base64(self):
        # Test the encoding function
        encoded_image = encode_image_base64(self.image_path)
        self.assertIsInstance(encoded_image, str)
        self.assertTrue(len(encoded_image) > 0)
        self.assertTrue(
            encoded_image.startswith("/9j/")
        )  # Check if it starts with the JPEG base64 prefix

    def tearDown(self):
        # Clean up by removing the test image
        if os.path.exists(self.image_path):
            os.remove(self.image_path)


if __name__ == "__main__":
    unittest.main()
