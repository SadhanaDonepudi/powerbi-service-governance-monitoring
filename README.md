# Power BI Service Governance & Refresh Monitoring

> ⚠️ **SYNTHETIC DATA / SIMULATED API** — No real Power BI tenant. The REST API and
> activity-log extracts under `data/` are deterministically simulated (seed 42).

## Overview
Governance + refresh-health monitoring across Power BI workspaces: simulated REST-API
inventory (workspaces, apps, audiences, datasets with owners, access), refresh-history
analytics, alerting rules for failed/slow refreshes, a gateway troubleshooting
runbook, and dev/test/prod deployment-pipeline templates.

## Architecture
`src/simulate_powerbi_api.py` → `data/` (JSON/CSV) → `src/governance_monitor.py` +
`src/alerting.py` → `outputs/`. Simulated polling interval: 15 minutes.

## How to run
```bash
python src/simulate_powerbi_api.py
python src/governance_monitor.py
python src/alerting.py
python -m pytest tests/ -q
```

## Results (actual run, synthetic)
- Workspaces: **62**; Apps: **40**; Audiences: **84** (186 total ≥ 60)
- Datasets: **189** (every dataset has an owner); refresh events: **5,670**
- Failed refreshes: **306 (5.40%)**
- Alerts: **575** — 306 critical (failed), 269 warning (slow, duration > p95 = 59.88 min)
- Simulated detection latency — automated 15-min polling: **median 8.0 min, p95 15 min**;
  manual daily 09:00 review: **median 689 min, p95 1,373 min**. The design polls every
  15 minutes (vs daily manual review); the figures above are this simulation's real
  outputs, not live-tenant numbers.

## Docs
`docs/api_simulation.md` (endpoint mapping), `docs/gateway_troubleshooting_runbook.md`,
`docs/deployment_pipeline_guide.md` + `deployment_pipelines/*.json`.
