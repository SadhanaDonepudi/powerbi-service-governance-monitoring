"""Deterministic SYNTHETIC simulation of the Power BI REST API + Activity Log.

No real Power BI tenant is contacted. Outputs REST-API-shaped JSON and an
activity-log CSV under data/. Fixed seed 42.
"""
import csv, json, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

WS_NAMES = ["Finance Reporting","Sales Analytics","HR People Metrics","Operations Control","Supply Chain Insights","Marketing Funnels","Customer Success","Risk & Compliance","Clinical Quality","Executive Dashboards","Product Telemetry","Revenue Assurance","Inventory Planning","Procurement Spend","Support Analytics","Data Quality Lab","Field Service","Pricing Analytics","Forecast Studio","Governance Sandbox"]
DOMAINS = ["Finance","Sales","HR","Ops","SupplyChain","Marketing"]
OWNERS = [f"owner{i:02d}@example.com" for i in range(1, 21)]
USERS = [f"user{i:03d}@contoso.example" for i in range(1, 151)]

def iso(dt): return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)

    # 62 workspaces ids
    workspaces, datasets, reports, access = [], [], [], []
    did = 0
    rid = 0
    for wi in range(62):
        ws_id = f"ws-{wi+1:03d}"
        name = f"{WS_NAMES[wi % len(WS_NAMES)]} {wi+1}" if wi >= len(WS_NAMES) else WS_NAMES[wi]
        workspaces.append({"id": ws_id, "name": name, "type": "Workspace",
                           "state": "Active", "isReadOnly": False})
        # 2-4 datasets per workspace
        for _ in range(random.randint(2, 4)):
            did += 1
            ds_id = f"ds-{did:04d}"
            datasets.append({"id": ds_id, "name": f"{name} Dataset {did}",
                             "workspaceId": ws_id,
                             "configuredBy": random.choice(OWNERS),
                             "isRefreshable": True,
                             "webUrl": f"https://app.powerbi.com/groups/{ws_id}/datasets/{ds_id}"})
            rid += 1
            reports.append({"id": f"rpt-{rid:04d}", "name": f"{name} Report {rid}",
                            "datasetId": ds_id, "workspaceId": ws_id,
                            "reportType": "PowerBIReport",
                            "webUrl": f"https://app.powerbi.com/groups/{ws_id}/reports/rpt-{rid:04d}"})
        # access grants
        for _ in range(random.randint(3, 8)):
            access.append({"workspaceId": ws_id, "identifier": random.choice(USERS),
                           "principalType": "User",
                           "groupUserAccessRight": random.choice(["Admin","Member","Contributor","Viewer"])})

    apps, audiences = [], []
    for wi, ws in enumerate(workspaces[:40]):
        app_id = f"app-{wi+1:03d}"
        apps.append({"id": app_id, "name": f"{ws['name']} App",
                     "workspaceId": ws["id"], "publishedBy": random.choice(OWNERS),
                     "lastUpdate": iso(start + timedelta(days=random.randint(0, 60)))})
        for ai in range(random.randint(1, 3)):
            audiences.append({"id": f"aud-{wi+1:03d}-{ai+1}", "appId": app_id,
                              "name": f"Audience {ai+1}",
                              "accessRight": "Read"})

    json.dump({"value": workspaces}, open(DATA/"workspaces.json","w"), indent=2)
    json.dump({"value": datasets}, open(DATA/"datasets.json","w"), indent=2)
    json.dump({"value": reports}, open(DATA/"reports.json","w"), indent=2)
    json.dump({"value": apps}, open(DATA/"apps.json","w"), indent=2)
    json.dump({"value": audiences}, open(DATA/"audiences.json","w"), indent=2)
    json.dump({"value": access}, open(DATA/"access.json","w"), indent=2)

    # Refresh history: 30 days per dataset
    refreshes = []
    for ds in datasets:
        for d in range(30):
            t = start + timedelta(days=d, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            dur = random.lognormvariate(3.2, 0.5)  # minutes
            roll = random.random()
            if roll < 0.05:
                status, dur = "Failed", round(dur, 2)
            elif roll < 0.08:
                status, dur = "Completed", round(dur * 2.5, 2)  # slow
            else:
                status, dur = "Completed", round(dur, 2)
            refreshes.append({"datasetId": ds["id"], "workspaceId": ds["workspaceId"],
                              "requestId": f"req-{len(refreshes)+1:06d}",
                              "refreshType": random.choice(["Scheduled","OnDemand"]),
                              "startTime": iso(t), "endTime": iso(t + timedelta(minutes=dur)),
                              "status": status, "durationMinutes": dur})
    json.dump({"value": refreshes}, open(DATA/"refreshes.json","w"), indent=2)

    # Activity log CSV
    with open(DATA/"activity_log.csv","w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["Id","CreationTime","Operation","UserKey","UserId","WorkspaceId","DatasetId","ReportId","CapacityId","ObjectType"])
        n = 1
        for _ in range(5000):
            t = start + timedelta(days=random.randint(0, 29), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            ds = random.choice(datasets)
            op = random.choices(["View","ViewReport","Export","RefreshDataset","ViewDashboard"], weights=[60,25,5,5,5])[0]
            w.writerow([f"act-{n:06d}", iso(t), op, f"key-{n}", random.choice(USERS),
                        ds["workspaceId"], ds["id"], "", "", "Dataset"])
            n += 1
    print(f"workspaces={len(workspaces)} datasets={len(datasets)} reports={len(reports)} "
          f"apps={len(apps)} audiences={len(audiences)} refreshes={len(refreshes)} access={len(access)}")

if __name__ == "__main__": main()
