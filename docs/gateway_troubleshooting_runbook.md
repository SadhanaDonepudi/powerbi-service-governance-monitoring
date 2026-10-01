# Gateway Troubleshooting Runbook
| Symptom | Likely causes | Checks | Fixes |
|---|---|---|---|
| Scheduled refresh fails "gateway offline" | Gateway service stopped; host rebooted | Gateway status in Service; Windows Service "On-premises data gateway" | Restart service; set to Automatic; check network |
| "Credentials are missing / expired" | OAuth token expiry; password rotation | Test connection on dataset Settings | Re-enter credentials; use service principal |
| Data source mismatch | Gateway data source name/path differs from PBIX | Compare PBIX connection vs gateway mapping | Add matching data source; remap dataset |
| Mashup engine error | M-query / driver issue | Refresh history error detail; gateway logs | Update gateway; fix query; check drivers |
| Slow refresh > p95 | Large model, no incremental refresh, gateway CPU | Duration trend in refresh_health.csv; gateway perf counters | Enable incremental refresh; scale gateway host |
| Timeout | Long-running source query | Source query duration; gateway timeout settings | Optimize query; split model |
| "DM_GWPipeline_GatewayDataSourceAccessError" | User lacks data-source permission | Gateway datasource Users tab | Grant user access on the data source |
| Endorsement/certification stale | Governance drift | Workspace inventory review | Re-certify in workspace settings |

Escalation: capture requestId from refresh history, gateway logs, and the alert JSON before contacting support.
