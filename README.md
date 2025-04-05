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

## Web Interface

Run the report generation and create the summaries by launching the web interface.

```shell
OCM_TOKEN=$(ocm token) uv run streamlit run Incident\ Report.py
```
After running the two commands to generate the reports and summaries, view it in a browser with `uv run streamlit run ❗Incident\ Report.py`.

## Inspection

The reports and summaries can be found in ./incident-reports and ./incident-summaries
