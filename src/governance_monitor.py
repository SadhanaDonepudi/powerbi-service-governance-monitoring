"""Governance monitor — loads simulated extracts, writes outputs/."""
import json, statistics
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
DATA, OUT = BASE/"data", BASE/"outputs"

def load(n): return json.loads((DATA/n).read_text())["value"]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ws = load("workspaces.json"); ds = load("datasets.json"); apps = load("apps.json")
    auds = load("audiences.json"); access = load("access.json")
    rfs = load("refreshes.json")

    inv = ["workspaceId,workspaceName,datasetCount,reportCount,hasApp"]
    ds_by_ws = Counter(d["workspaceId"] for d in ds)
    app_ws = {a["workspaceId"] for a in apps}
    for w in ws:
        inv.append(f"{w['id']},{w['name']},{ds_by_ws.get(w['id'],0)},0,{w['id'] in app_ws}")
    (OUT/"workspace_inventory.csv").write_text("\n".join(inv)+"\n")

    by_ds = {}
    for r in rfs: by_ds.setdefault(r["datasetId"], []).append(r)
    lines = ["datasetId,totalRefreshes,successCount,failureCount,successRate,avgDurationMin,p95DurationMin,maxDurationMin"]
    for d in ds:
        rs = by_ds.get(d["id"], [])
        succ = sum(1 for r in rs if r["status"]=="Completed")
        durs = sorted(r["durationMinutes"] for r in rs)
        p95 = durs[int(0.95*(len(durs)-1))] if durs else 0
        lines.append(f"{d['id']},{len(rs)},{succ},{len(rs)-succ},{succ/len(rs) if rs else 0:.4f},"
                     f"{statistics.mean(durs) if durs else 0:.2f},{p95:.2f},{max(durs) if durs else 0:.2f}")
    (OUT/"refresh_health.csv").write_text("\n".join(lines)+"\n")

    acc = ["userId,workspaceId,accessRight"]
    for a in access: acc.append(f"{a['identifier']},{a['workspaceId']},{a['groupUserAccessRight']}")
    (OUT/"access_matrix.csv").write_text("\n".join(acc)+"\n")

    import csv, io
    raw = (DATA/"activity_log.csv").read_text()
    ops = Counter(r["Operation"] for r in csv.DictReader(io.StringIO(raw)))
    top = Counter((r.get("DatasetId") or "") for r in csv.DictReader(io.StringIO(raw))).most_common(5)
    total = sum(len(v) for v in by_ds.values())
    fails = sum(1 for r in rfs if r["status"]=="Failed")
    md = (f"# Usage Summary (SYNTHETIC)\n\n- Workspaces: {len(ws)}\n- Datasets: {len(ds)}\n"
          f"- Apps: {len(apps)}\n- Audiences: {len(auds)}\n- Total refreshes: {total}\n"
          f"- Failed refreshes: {fails} ({fails/total*100:.2f}%)\n\n## Activity operations\n"
          + "\n".join(f"- {k}: {v}" for k,v in ops.most_common())
          + "\n\n## Top datasets by views\n" + "\n".join(f"- {k}: {v}" for k,v in top if k) + "\n")
    (OUT/"usage_summary.md").write_text(md)
    print(md)

if __name__ == "__main__": main()
