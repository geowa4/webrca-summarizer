# WebRCA Summarizer

## Prerequisites

- Installed [ocm-cli](https://console.redhat.com/openshift/downloads)
- Logged in (`ocm login --use-auth-code`)
- Python 3.12
- Installed uv for Python package management (`pip install uv`)

## Creating Incident Reports

Run `uv run gen-incident-reports.py $(ocm token)` to create reports in incident-reports/.
Each report will be named after its ID.

## OpenAI-Compatible API

To use the summarization code, you will need an OpenAI-compatible API.
The current code is written assume [LM Studio](https://lmstudio.ai/) with Gemma 3 27b loaded.
If you are using ollama or another service, change the `OpenAIModel` configuration in main.py.

Depending on how much text was added to each of the events, the context length may need to be raised to accomodate.
I run with 8096.

Run `uv run gen-sumaries.py` to write the summaries for each incident to incident-summaries/.
