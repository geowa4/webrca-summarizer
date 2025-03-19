#!/usr/bin/env bash

incidents=$(ocm get /api/web-rca/v1/incidents \
  --parameter order_by="created_at desc" --parameter size="50" | \
  jq -rc '.items | map(select((.updated_at | gsub("\\.(\\d)+Z"; "Z") | fromdateiso8601) >= (now - 7 * 86400)))')

rm -rf incident-reports
mkdir -p incident-reports

echo -n "$incidents" | jq -rc '.[]' | \
while IFS= read -r incident
do
  invalid=$(echo -n "$incident" | jq -rc '.invalid')
  if [ "$invalid" = "true" ]
  then
    continue
  fi
  id=$(echo -n "$incident" | jq -rc '.id')
  incident_id=$(echo -n "$incident" | jq -rc '.incident_id')
  echo incident-reports/"$incident_id"_"$id".md
  rm -f incident-reports/"$incident_id"_"$id".md
  touch incident-reports/"$incident_id"_"$id".md
  incident_format_string=$(cat << EOF
. | "# \(.incident_id): \(.summary)

Products:  \(.products | join(", "))
Status:    \(.status)
Severity:  \(.severity)
Created:   \(.created_at)
Updated:   \(.updated_at)
Manager:   \(.responsible_manager.name)
Commander: \(.incident_commander.name)
Slack:     https://app.slack.com/client/\(.slack_workspace_id)/\(.slack_channel_id)

## Description

\(.description)
"
EOF
)
  incident_as_text=$(
    echo -n "$incident" | \
    jq -rc "$incident_format_string"
  )
  echo "$incident_as_text" >> incident-reports/"$incident_id"_"$id".md

  event_text=$(ocm get /api/web-rca/v1/incidents/"$id"/events | \
    jq -rc '[.items[] | select(.creator.id != "00000000-0000-0000-0000-000000000000" and .note != null)] | .[-3:] | .[]' | \
    jq -rc '. | "- [\(.occurred_at) from \(.creator.name)]\n  \(.note | gsub("\n"; "\n  "))"')
  # echo >> incident-reports/"$incident_id"_"$id".md
  printf '\n## Events:\n' >> incident-reports/"$incident_id"_"$id".md
  # echo >> incident-reports/"$incident_id"_"$id".md
  echo "$event_text" >> incident-reports/"$incident_id"_"$id".md
done

