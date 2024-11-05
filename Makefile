# Variables
VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
REQUIREMENTS = requirements.txt
SCRIPT = main.py
PARSE_SCRIPT = parse_and_call_openai.py

# Default target
.PHONY: all
all: install

# Create a virtual environment
.PHONY: create-venv
create-venv:
	python3 -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)"

# Install dependencies
.PHONY: install
install: create-venv
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)
	@echo "Dependencies installed"

# Run the script
.PHONY: run
run:
	$(PYTHON) $(SCRIPT)

# Run the parse_and_call_openai script
.PHONY: run-parse
run-parse:
	$(PYTHON) $(PARSE_SCRIPT)

# Run individual tests
.PHONY: test-encode-image-base64
test-encode-image-base64:
	$(PYTHON) -m unittest tests/test_encode_image_base64.py
	@echo "Test for upload_image completed"

.PHONY: test-create-jsonl
test-create-jsonl:
	$(PYTHON) -m unittest tests/test_create_jsonl.py
	@echo "Test for create_jsonl completed"

.PHONY: test-upload-jsonl
test-upload-jsonl:
	$(PYTHON) -m unittest tests/test_upload_jsonl.py
	@echo "Test for upload_jsonl completed"

.PHONY: test-create-batch
test-create-batch:
	$(PYTHON) -m unittest tests/test_create_batch.py
	@echo "Test for create_batch completed"

.PHONY: test-retrieve-batch-results
test-retrieve-batch-results:
	$(PYTHON) -m unittest tests/test_retrieve_batch_results.py
	@echo "Test for retrieve_batch_results completed"

.PHONY: test-upload-to-google-sheets
test-upload-to-google-sheets:
	$(PYTHON) -m unittest tests/test_upload_to_google_sheets.py
	@echo "Test for upload_to_google_sheets completed"

# Run all tests
.PHONY: test
test: test-upload-image test-create-jsonl test-upload-jsonl test-create-batch test-retrieve-batch-results test-upload-to-google-sheets

# Clean up generated files
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	rm -f tasks.jsonl evaluation_results.csv
	@echo "Cleaned up generated files and virtual environment"