"""Alerting rules + simulated detection-latency comparison (SYNTHETIC data)."""
import json, statistics
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
DATA, OUT = BASE/"data", BASE/"outputs"
POLL_MINUTES = 15  # design polling interval

def parse(ts): return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rfs = json.loads((DATA/"refreshes.json").read_text())["value"]
    durs = sorted(r["durationMinutes"] for r in rfs)
    p95 = durs[int(0.95*len(durs))]
    print(f"p95 duration threshold: {p95:.2f} min")

    alerts, auto_lat, manual_lat = [], [], []
    for r in rfs:
        end = parse(r["endTime"])
        if r["status"] == "Failed":
            sev = "critical"
        elif r["durationMinutes"] > p95:
            sev = "warning"
        else:
            continue
        # automated: next 15-min poll boundary after event end
        mins_into_hour = end.minute % POLL_MINUTES
        wait = (POLL_MINUTES - mins_into_hour) if mins_into_hour else 0
        auto_lat.append(wait + 1)  # +1 min processing
        # manual: daily review at 09:00 -> minutes until next 09:00
        manual_lat.append((24*60 - (end.hour*60 + end.minute - 540)) % (24*60) or 1440)
        alerts.append({"datasetId": r["datasetId"], "severity": sev, "status": r["status"],
                       "durationMinutes": r["durationMinutes"], "endTime": r["endTime"],
                       "message": "Refresh FAILED" if sev=="critical" else f"Slow refresh {r['durationMinutes']}m > p95 {p95:.1f}m"})

    json.dump({"p95ThresholdMinutes": round(p95,2), "alerts": alerts}, open(OUT/"alerts.json","w"), indent=2)
    counts = Counter(a["severity"] for a in alerts)
    med_a, med_m = statistics.median(auto_lat), statistics.median(manual_lat)
    def p95v(xs): xs=sorted(xs); return xs[int(0.95*len(xs))]
    summary = (f"# Alert Summary (SYNTHETIC)\n\n- Total alerts: {len(alerts)}\n"
               f"- Critical (failed): {counts.get('critical',0)}\n- Warning (slow, >p95={p95:.2f}m): {counts.get('warning',0)}\n\n"
               f"## Simulated detection latency\n- Automated (15-min polling): median {med_a} min, p95 {p95v(auto_lat)} min\n"
               f"- Manual (daily 09:00 review): median {med_m} min, p95 {p95v(manual_lat)} min\n\n"
               f"Note: the automated design polls every 15 minutes; the observed simulated median detection\n"
               f"latency is {med_a} minutes (event -> next poll + processing), versus a simulated manual\n"
               f"median of {med_m} minutes. Figures are from this synthetic simulation, not a live tenant.\n")
    (OUT/"alert_summary.md").write_text(summary)
    print(summary)

if __name__ == "__main__": main()
