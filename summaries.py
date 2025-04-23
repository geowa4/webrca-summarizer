"""Summarizes each incident report."""

import logging
import os
from pathlib import Path
from pydantic import BaseModel
from dataclasses import dataclass, field

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROMPTS_DIR = Path("prompts")
SUMMARIZATION_PROMPT_PATH = PROMPTS_DIR / "summarization"
EDITOR_PROMPT_PATH = PROMPTS_DIR / "editor"


@dataclass
class SummaryContext:
    retry_count: int = field(default=0)
    max_retries: int = field(default=1)


class EditorResponse(BaseModel):
    is_acceptable: bool
    feedback: str


class SummaryResponse(BaseModel):
    content: str


editor_agent = Agent(
    OpenAIModel(
        os.getenv("EDITOR_MODEL_NAME", "gemma-3-27b-it"),
    ),
    system_prompt=EDITOR_PROMPT_PATH.read_text(),
    output_type=EditorResponse,
)

summarization_agent = Agent(
    OpenAIModel(
        os.getenv("SUMMARIZATION_MODEL_NAME", "gemma-3-27b-it"),
    ),
    retries=2,
    system_prompt=SUMMARIZATION_PROMPT_PATH.read_text(),
    output_type=SummaryResponse,
    deps_type=SummaryContext,
)


@summarization_agent.output_validator
def validate_summary(
    ctx: RunContext[SummaryContext], summary: SummaryResponse
) -> SummaryResponse:
    logger.info(
        f"Validating generated summary (attempt {ctx.deps.retry_count + 1}):\n{summary.content}"
    )
    editor_response = editor_agent.run_sync(summary.content)
    if not editor_response.output.is_acceptable:
        if ctx.deps.retry_count >= ctx.deps.max_retries:
            logger.warning(
                f"Max retries ({ctx.deps.max_retries}) reached. Using last generated summary. "
                f"Feedback: {editor_response.output.feedback}"
            )
            return summary
        logger.warning(
            f"Summary not acceptable. Feedback: {editor_response.output.feedback}"
        )
        ctx.deps.retry_count += 1
        raise ModelRetry(
            f"Summary not acceptable. Feedback: {editor_response.output.feedback}"
        )
    
    logger.info("Summary validated successfully")
    return summary


def summarize_reports(report_dir: Path, summary_dir: Path) -> None:
    """Summarizes all incident-reports."""
    if not report_dir.exists() or not report_dir.is_dir():
        logger.critical(
            "Directory %s does not exist or is not a directory.", report_dir
        )
        return
    summary_dir.mkdir(exist_ok=True)
    logger.info(f"Processing reports from {report_dir} to {summary_dir}")

    for file_path in report_dir.glob("*.md"):
        summary_path = summary_dir / file_path.name
        if summary_path.exists():
            logger.info(f"Skipping {file_path} - summary already exists")
            continue

        logger.info(f"Processing file: {file_path}")
        with file_path.open("r", encoding="utf-8") as file:
            content = file.read()
            logger.debug(f"Read {len(content)} characters from {file_path}")

        try:
            logger.info("Generating summary")
            summary = summarization_agent.run_sync(content, deps=SummaryContext())
            logger.info("Summary generated successfully")
            
            summary_path.write_text(summary.output.content)
            logger.info(f"Summary written to {summary_path}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}", exc_info=True)
            continue


if __name__ == "__main__":
    from settings import REPORTS_DIR, SUMMARY_DIR

    logger.info("Starting summarization process")
    summarize_reports(REPORTS_DIR, SUMMARY_DIR)
    logger.info("Summarization process completed")
