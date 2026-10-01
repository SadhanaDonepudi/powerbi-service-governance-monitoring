# API Simulation Mapping (SYNTHETIC)

All files mimic the real Power BI REST API / Activity Log shapes. No live tenant.

| File | Real endpoint / source mimicked |
|---|---|
| workspaces.json | `GET /v1.0/myorg/groups` — `{value:[{id,name,type,state,isReadOnly}]}` |
| datasets.json | `GET /v1.0/myorg/groups/{id}/datasets` — id, name, configuredBy (owner), isRefreshable, webUrl |
| reports.json | `GET /v1.0/myorg/groups/{id}/reports` |
| apps.json | `GET /v1.0/myorg/apps` |
| audiences.json | App audiences (Admin API `GET /v1.0/myorg/admin/groups` expand) |
| access.json | `GET /v1.0/myorg/groups/{id}/users` — identifier, principalType, groupUserAccessRight |
| refreshes.json | `GET /v1.0/myorg/groups/{id}/datasets/{id}/refreshes` — requestId, refreshType, startTime, endTime, status |
| activity_log.csv | Microsoft 365 Activity Log: Id, CreationTime, Operation, UserId, WorkspaceId, DatasetId |

Sample refresh payload:
```json
{"datasetId":"ds-0001","refreshType":"Scheduled","status":"Completed",
 "startTime":"2026-06-05T03:12:00Z","durationMinutes":4.2}
```
