import unittest
from main import upload_to_google_sheets, EvaluationResponse


class TestUploadToGoogleSheets(unittest.TestCase):
    def test_upload_to_google_sheets(self):
        # Create dummy data for testing
        responses = [
            EvaluationResponse(
                Name="Test Author",
                Strengths_and_Weaknesses=3,
                Emotions_Recognition=2,
                Identity_Value=3,
            )
        ]
        try:
            upload_to_google_sheets(responses)
            result = True
        except Exception as e:
            print(f"Google Sheets upload failed: {e}")
            result = False

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
