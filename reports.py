"""Creates simple Markdown incident reports."""

from datetime import datetime, timedelta, timezone
import logging
from pathlib import Path
import sys

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def gen_reports(reports_dir: Path, ocm_token: str) -> None:
    incidents = [
        i
        for i in requests.get(
            "https://api.openshift.com/api/web-rca/v1/incidents?page=1&size=50&order_by=created_at%20desc&invalid=false",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {ocm_token}",
            },
        ).json()["items"]
        if datetime.fromisoformat(i["created_at"])
        >= (datetime.now(timezone.utc) - timedelta(days=10))
    ]

    reports_dir.mkdir(exist_ok=True)

    for incident in incidents:
        logger.info(incident["incident_id"])
        # load all events, sorted by created desc
        events = requests.get(
            f"https://api.openshift.com/api/web-rca/v1/incidents/{incident['id']}/events?order_by=created_at%20desc",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {ocm_token}",
            },
        ).json()["items"]

        # generate events text for first (most recent) events
        events_text = "\n".join([
            f"- [{e['occurred_at']} from {e['creator']['name']}]\n  {e['note'].replace('\n', '\n  ')}"
            for e in events
            if e["creator"]["id"] != "00000000-0000-0000-0000-000000000000"
            and e["note"] is not None
        ][:3])

        # write report to a file
        report = reports_dir / f"{incident['incident_id']}.md"

        report_text = (
            f"# {incident['incident_id']}: {incident['summary']}\n"
            "\n"
            "| Key       | Value |\n"
            "| --------- | ----- |\n"
            f"| Products  | {', '.join(incident['products'])} |\n"
            f"| Status    | {incident['status']} |\n"
            f"| Severity  | {incident['severity']} |\n"
            f"| Created   | {incident['created_at']} |\n"
            f"| Updated   | {incident['updated_at']} |\n"
            f"| Manager   | {incident.get('responsible_manager', {}).get('name')} |\n"
            f"| Commander | {incident.get('incident_commander', {}).get('name')} |\n"
            f"| Slack     | https://app.slack.com/client/{incident.get('slack_workspace_id')}/{incident.get('slack_channel_id')} |\n"
            "\n"
            "## Description\n"
            "\n"
            f"{incident['description']}\n"
            "\n"
            "## Events\n"
            "\n"
            f"{events_text}"
        )
        report.write_text(report_text)


if __name__ == "__main__":
    from os import getenv
    from .settings import REPORTS_DIR
    gen_reports(REPORTS_DIR, getenv("OCM_TOKEN"))
