import json, sys
from pathlib import Path
B = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(B/"src"))
def load(n): return json.loads((B/"data"/n).read_text())["value"]
def test_counts():
    assert len(load("workspaces.json")) >= 60
def test_owners():
    assert all(d["configuredBy"] for d in load("datasets.json"))
def test_refresh_all():
    ds = {d["id"] for d in load("datasets.json")}
    rf = {r["datasetId"] for r in load("refreshes.json")}
    assert ds <= rf
def test_alerts_fire():
    a = json.loads((B/"outputs"/"alerts.json").read_text())
    assert a["alerts"], "expected seeded failures/slows"
    assert any(x["severity"]=="critical" for x in a["alerts"])
