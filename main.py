"""Summarizes each text file."""

import logging
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEXT_DIR = Path("incident-reports")

agent = Agent(
    OpenAIModel(
        "gemma-3-27b-it",
        #"qwq-32b",
        base_url="http://127.0.0.1:1234/v1",
    ),
    system_prompt=(
        "You are an assistant who must summarize the user-provided incident report into an executive summary of 2-3 sentences. "
        "Use an active voice only, and clearly state the product, the impact to the customer, the most recent situation, and, if included, the customer's name. "
        "If the customer's name is unknow, state 'Unknown Customer'.\n"
        "\n"
        "The text you are given describes an incident declared in an organization of Site Reliability Engineers supporting a fleet of OpenShift clusters. "
        "The input format is markdown. The format is as follows.\n"
        "\n"
        "# INCIDENT ID: TITLE\n"
        "\n"
        "DESCRIPTION\n"
        "\n"
        "Events:\n"
        "\n"
        "[TIMESTAMP] LIST OF EVENTS"
        "\n"
        "When responding, reply with markdown using the following format.\n"
        "\n"
        "[CUSTOMER NAME, PRODUCTS] executive summary ([INCIDENT ID](SLACK LINK))\n"
    ),
)


def main() -> None:
    """Summarizes all text files in the text dir."""
    if not TEXT_DIR.exists() or not TEXT_DIR.is_dir():
        logger.critical("Directory %s does not exist or is not a directory.", TEXT_DIR)
        return

    summaries = []
    for file_path in TEXT_DIR.glob("*.md"):
        logger.info(f"Summarizing {file_path}")
        with file_path.open("r", encoding="utf-8") as file:
            content = file.read()

        summary = agent.run_sync(content)

        summaries.append(f"Summary of {file.name}:\n{summary.data}\n")

    print(f"{'-' * 50}\n".join(summaries))


if __name__ == "__main__":
    main()
