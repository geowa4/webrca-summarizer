# WebRCA Summarizer

## Prerequisites

- Installed [ocm-cli](https://console.redhat.com/openshift/downloads)
- Logged in (`ocm login --use-auth-code`)
- Python 3.12
- Installed uv for Python package management (`pip install uv`)

## OpenAI-Compatible API

To use the summarization code, you will need an OpenAI-compatible API.
The current code is written assuming [LM Studio](https://lmstudio.ai/) is running and Gemma 3 27b is loaded.
If you are using ollama or another service, change the `OpenAIModel` configuration in main.py.

Depending on how much text was added to each of the events, the context length may need to be raised to accomodate.
I run with 8096.

## Environment Variables

These variables must suit your environment.
Examples are provided here for what I have most recently used.

```shell
export OPENAI_API_KEY="lm-studio" OPENAI_BASE_URL="http://127.0.0.1:1234/v1" OCM_TOKEN=$(ocm token)
export SUMMARIZATION_MODEL_NAME=mistral-small-3.1-24b-instruct-2503 EDITOR_MODEL_NAME=mistral-small-3.1-24b-instruct-2503
```

## Single Commands

The reports and summaries can be generated easily in your shell.

```shell
uv run reports.py
uv run summaries.py
```

## Web Interface

If you wish to print to PDF or view the reports in your browser, launch the web interface with Streamlit.

```shell
uv run streamlit run Incident\ Report.py
```

## Inspection

The reports and summaries can be found in ./incident-reports and ./incident-summaries
