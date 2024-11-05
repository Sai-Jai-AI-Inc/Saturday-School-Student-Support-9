import openai
import json
import os
import time
import base64
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Annotated
from typing import List
from dotenv import load_dotenv
from tqdm import tqdm
import gspread

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

# Set OpenAI API key
openai.api_key = API_KEY

# Pydantic model for the expected response format
class EvaluationResponse(BaseModel):
    Name: Annotated[str, Field(min_length=1)]
    Strengths_and_Weaknesses: Annotated[int, Field(ge=0, le=3)]
    Emotions_Recognition: Annotated[int, Field(ge=0, le=3)]
    Identity_Value: Annotated[int, Field(ge=0, le=3)]


# Step 1: Encode images to base64
def encode_image_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


# Step 2: Create a .jsonl file for batch processing
def create_jsonl(image_files):
    jsonl_path = "tasks.jsonl"
    tasks = []

    # Define the system prompt used for categorization
    categorize_system_prompt = (
        "You are an evaluator who reviews the self-awareness content provided in the base64-encoded image. "
        "Assess the image content and provide structured feedback based on the given criteria."
    )

    for index, image_file in enumerate(image_files):
        # Encode the image to base64 format
        encoded_image = encode_image_base64(image_file)
        image_data_url = f"data:image/jpeg;base64,{encoded_image}"

        # Create the description with the encoded image
        description = {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_data_url}},
                {
                    "type": "text",
                    "text": (
                        "Evaluate the self-awareness skills of the author by reviewing the content in the provided image.\n\n"
                        "Use the following criteria:\n"
                        "1. Identify and articulate their strengths and weaknesses.\n"
                        "2. Recognize and express their emotions appropriately.\n"
                        "3. Understand and value their own identity and beliefs.\n\n"
                        "For each component, score the author from 0 to 3 according to the rubric:\n"
                        "- 0: Unable to identify/express strengths, weaknesses, or emotions; lacks self-awareness.\n"
                        "- 1: Identifies or expresses these aspects partially but lacks depth or consistency.\n"
                        "- 2: Articulates and understands most aspects with room for improvement.\n"
                        "- 3: Clearly and comprehensively articulates strengths, weaknesses, emotions, and identity.\n\n"
                        "Ensure the response is structured to match the following JSON format:\n"
                        "{\n"
                        '  "Name": "Author Name",\n'
                        '  "Strengths_and_Weaknesses": <score>,\n'
                        '  "Emotions_Recognition": <score>,\n'
                        '  "Identity_Value": <score>\n'
                        "}\n"
                        "Replace <score> with an integer value between 0 and 3."
                    ),
                },
            ],
        }

        # Create the task with the provided structure
        task = {
            "custom_id": f"task-{index}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o",
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": categorize_system_prompt},
                    description,
                ],
            },
        }

        tasks.append(task)

    # Save tasks to a JSONL file
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(json.dumps(task) + "\n")

    return jsonl_path

# Step 3: Upload .jsonl file
def upload_jsonl(jsonl_path):
    with open(jsonl_path, "rb") as file:
        response = openai.files.create(file=file, purpose="batch")
    return response

# Step 4: Create a batch request
def create_batch(file_id):
    response = openai.batches.create(
        input_file_id=file_id, endpoint="/v1/chat/completions", completion_window="24h"
    )
    return response


# Step 5: Retrieve batch results and validate with Pydantic
def retrieve_batch_results(batch_id):
    with tqdm(
        total=100,
        desc="Waiting for batch completion",
        bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} [{elapsed}]",
    ) as pbar:
        while True:
            try:
                response = openai.batches.retrieve(batch_id)
                print(
                    f"Batch status: {response.status}"
                )  # Debug statement to print the current status

                if response.status == "complete":
                    pbar.update(100 - pbar.n)  # Complete the progress bar
                    break
                elif response.status == "failed":
                    raise Exception("Batch processing failed")

                raise Exception("Batch processing not complete")

            except Exception as e:
                print(f"Exception caught: {e}")  # Debug information
                time.sleep(10)  # Wait 10 seconds before trying again
                pbar.update(10)  # Update progress to indicate waiting

    # Validate each response line with Pydantic
    validated_responses = []
    result_file_id = response.output_file_id
    result_file_content = openai.files.content(result_file_id).content
    result_file_name = "results.jsonl"

    with open(result_file_name, "wb") as file:
        file.write(result_file_content)
    with open(result_file_name, "r") as results:
        for result in results:
            try:
                validated_response = EvaluationResponse.model_validate_json(result)
                validated_responses.append(validated_response)
            except ValidationError as e:
                print("Validation Error:", e)

    return validated_responses

# Step 6: Aggregate results and upload to Google Sheets
def upload_to_google_sheets(validated_responses):
    # Create a DataFrame from the validated responses
    data = [
        {
            "Name": response.Name,
            "Strengths and Weaknesses": response.Strengths_and_Weaknesses,
            "Emotions Recognition": response.Emotions_Recognition,
            "Identity Value": response.Identity_Value,
        }
        for response in validated_responses
    ]
    df = pd.DataFrame(data)

    # Export the DataFrame to a CSV file
    csv_path = "evaluation_results.csv"
    df.to_csv(csv_path, index=False)

    # Google Sheets setup using service account credentials
    client = gspread.service_account(filename="service_account.json")

    # Open an existing Google Sheet (create it manually or ensure it exists)
    sheet_name = "Self-Awareness Evaluation"
    spreadsheet = client.open(sheet_name)
    worksheet = spreadsheet.sheet1

    # Upload CSV content to Google Sheets
    with open(csv_path, "r", encoding="utf-8") as file:
        content = file.read()
        client.import_csv(spreadsheet.id, content)

    print(f"Results uploaded to Google Sheets: {spreadsheet.url}")

# Main function
if __name__ == "__main__":
    # Create list of image file paths from the "jj_images" folder
    image_folder = "jj_images"
    image_files = [
        os.path.join(image_folder, f)
        for f in os.listdir(image_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    # Create and upload JSONL file
    jsonl_path = create_jsonl(image_files)
    upload_response = upload_jsonl(jsonl_path)
    jsonl_file_id = upload_response.id

    # Create batch
    batch_response = create_batch(jsonl_file_id)
    batch_id = batch_response.id

    # Retrieve results
    results = retrieve_batch_results(batch_id)

    # Upload results to Google Sheets
    upload_to_google_sheets(results)
