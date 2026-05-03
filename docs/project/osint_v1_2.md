# OSINT v1.2 - Public Framework

Ocean Sentinel OSINT v1.2 defines the public rules for evidence collection, scenario publication, and dashboard transparency.

## Public Scope

- Use public or historical sources only.
- Separate scenario outputs from measured observations.
- Display source, status, freshness, decision state, limits, and uncertainty.
- Keep internal operations, administrative access, confidential configuration, and non-public procedures out of public documents.

## Anti-Ambiguity Rule

Every simulation must state:

```json
{
  "type": "SCENARIO",
  "shadow_mode": true,
  "alert_allowed": false,
  "decision_ready": false
}
```

## Decision Rule

Historical or expired data does not support an operational alert. Scenario outputs remain exploratory and non-decision-making until a separate human-reviewed decision process explicitly changes that status.

## Public Dashboard Requirements

- Say "Shadow mode / Non décisionnel" on scenario pages.
- Do not present a scenario as a measured observation.
- Link scenario templates to `/data/schema/scenario_template.schema.json`.
- Avoid publishing sensitive infrastructure details or operational procedures.
