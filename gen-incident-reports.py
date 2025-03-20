"""Creates simple Markdown incident reports."""

from datetime import datetime, timedelta, timezone
import logging
from pathlib import Path
import sys

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPORT_DIR = Path("incident-reports")


def main() -> None:
    incidents = [
        i
        for i in requests.get(
            "https://api.openshift.com/api/web-rca/v1/incidents?page=1&size=50&order_by=created_at%20desc&invalid=false",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {sys.argv[1]}",
            },
        ).json()["items"]
        if datetime.fromisoformat(i["updated_at"])
        >= (datetime.now(timezone.utc) - timedelta(days=7))
    ]

    REPORT_DIR.mkdir(exist_ok=True)

    for incident in incidents:
        # load all events, sorted by created desc
        events = requests.get(
            f"https://api.openshift.com/api/web-rca/v1/incidents/{incident['id']}/events?order_by=created_at%20desc",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {sys.argv[1]}",
            },
        ).json()["items"]
        # generate events text for first (most recent) events
        events_text = "\n".join([
            f"- [{e['occurred_at']} from {e['creator']['name']}]\n  {e['note'].replace('\n', '\n  ')}"
            for e in events[:3]
            if e["creator"]["id"] != "00000000-0000-0000-0000-000000000000"
            and e["note"] is not None
        ])
        # write report to a file
        report = REPORT_DIR / f"{incident['incident_id']}.md"
        with report.open("w", encoding="UTF-8") as r:
            logger.info(incident["incident_id"])

            report_text = (
                f"# {incident['incident_id']}: {incident['summary']}\n"
                "\n"
                f"Products:  {', '.join(incident['products'])}\n"
                f"Status:    {incident['status']}\n"
                f"Severity:  {incident['severity']}\n"
                f"Created:   {incident['created_at']}\n"
                f"Updated:   {incident['updated_at']}\n"
                f"Manager:   {incident.get('responsible_manager', {}).get('name')}\n"
                f"Commander: {incident.get('incident_commander', {}).get('name')}\n"
                f"Slack:     https://app.slack.com/client/{incident.get('slack_workspace_id')}/{incident.get('slack_channel_id')}\n"
                "\n"
                "## Description\n"
                "\n"
                f"{incident['description']}\n"
                "\n"
                "## Events\n"
                "\n"
                f"{events_text}"
            )
            logger.info(report_text)
            r.write(report_text)


if __name__ == "__main__":
    main()
