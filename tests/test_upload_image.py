import unittest
from main import upload_image


class TestUploadImage(unittest.TestCase):
    def test_upload_image(self):
        # Replace 'sample_image.jpg' with an actual image in jj_images folder for the test
        response = upload_image(
            "jj_images/LINE_ALBUM_SSSS8 Wealth management_241104_2.jpg"
        )
        self.assertIn("id", response)
        self.assertEqual(response["purpose"], "batch")


if __name__ == "__main__":
    unittest.main()
