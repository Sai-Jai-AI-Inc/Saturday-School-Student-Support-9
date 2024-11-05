import openai
import json
import csv
import os
import time
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

# Set OpenAI API key
openai.api_key = API_KEY

# Create an OpenAI client instance
client = openai


# Function to parse tasks from a JSONL file, call OpenAI API, and aggregate results
def parse_and_call_openai(tasks_file, output_csv="results.csv"):
    results = []

    with open(tasks_file, "r", encoding="utf-8") as file:
        for line in file:
            try:
                # Parse each line as a JSON object
                task = json.loads(line)
                body = task.get("body")
                if not body:
                    print(f"Invalid task format: {line}")
                    continue

                # Extract the base64 image data
                base64_image = None
                for content in body["messages"]:
                    if isinstance(content, dict) and content.get("role") == "user":
                        for item in content.get("content", []):
                            if item.get("type") == "image_url":
                                base64_image = item["image_url"]["url"]
                                break

                # Call OpenAI API using the extracted task body
                response = client.chat.completions.create(
                    model=body["model"],
                    messages=body["messages"],
                    temperature=body.get(
                        "temperature", 0.1
                    ),  # Default temperature set to 0.1
                )

                # Extract the content of the response
                response_content = response.choices[0].message.content

                # Append result to the list
                results.append(
                    {
                        "custom_id": task["custom_id"],
                        "response": response_content,
                        "base64_image": base64_image,
                    }
                )

                print(f"Processed {task['custom_id']}")
                time.sleep(1)  # Optional: sleep to avoid hitting rate limits

            except Exception as e:
                print(f"Error processing task {task.get('custom_id', 'unknown')}: {e}")

    # Write results to a CSV file
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["custom_id", "response", "base64_image"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print(f"Results have been written to {output_csv}")


# Main function
if __name__ == "__main__":
    tasks_file = "tasks.jsonl"  # Replace with the path to your tasks.jsonl file
    if not os.path.exists(tasks_file):
        raise FileNotFoundError(
            f"{tasks_file} not found. Ensure the file exists in the specified path."
        )

    parse_and_call_openai(tasks_file)
