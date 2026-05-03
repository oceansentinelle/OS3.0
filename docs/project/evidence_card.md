# Evidence Card - Public Template

Use this template for public evidence summaries attached to OSINT v1.2 scenarios.

## Identification

- Evidence ID:
- Scenario ID:
- Title:
- Public source:
- Source date:
- Retrieval date:

## Classification

- Evidence type: public / historical / derived
- Truth status: MEASURED / INFERRED / SIMULATED
- Freshness status: FRESH / STALE / EXPIRED / UNKNOWN
- Decision status: non-decision-making by default

## Required Scenario Flags

```json
{
  "type": "SCENARIO",
  "shadow_mode": true,
  "alert_allowed": false,
  "decision_ready": false
}
```

## Limits And Uncertainty

- Known limits:
- Missing variables:
- Uncertainty:
- Human review status:

## Public Safety Note

This evidence card is a transparency artifact. It must not include credentials, confidential paths, private infrastructure details, or non-public operational procedures.
