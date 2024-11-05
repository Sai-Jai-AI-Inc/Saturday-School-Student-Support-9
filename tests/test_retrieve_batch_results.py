import unittest
from unittest.mock import patch, MagicMock
import json
from main import retrieve_batch_results, EvaluationResponse
from pydantic import ValidationError


class TestRetrieveBatchResults(unittest.TestCase):
    @patch("main.openai.batches.retrieve")
    @patch("main.openai.files.content")
    def test_retrieve_batch_results(self, mock_file_content, mock_batch_retrieve):
        # Simulate the first two calls returning "in_progress" and then "complete"
        mock_batch_retrieve.side_effect = [
            MagicMock(status="in_progress"),
            MagicMock(status="in_progress"),
            MagicMock(status="complete", output_file_id="test_output_file_id"),
        ]

        # Create a mock content for the output file
        result_data = {
            "Name": "Test Author",
            "Strengths_and_Weaknesses": 3,
            "Emotions_Recognition": 2,
            "Identity_Value": 3,
        }
        mock_file_content.return_value = MagicMock(
            content=json.dumps(result_data).encode("utf-8")
        )

        # Run the function and assert that it handles the transition to "complete"
        validated_responses = retrieve_batch_results("test_batch_id")

        # Check that the validated responses are as expected
        self.assertEqual(len(validated_responses), 1)
        self.assertIsInstance(validated_responses[0], EvaluationResponse)
        self.assertEqual(validated_responses[0].Name, "Test Author")
        self.assertEqual(validated_responses[0].Strengths_and_Weaknesses, 3)
        self.assertEqual(validated_responses[0].Emotions_Recognition, 2)
        self.assertEqual(validated_responses[0].Identity_Value, 3)


if __name__ == "__main__":
    unittest.main()
