# Alert Summary (SYNTHETIC)

- Total alerts: 575
- Critical (failed): 306
- Warning (slow, >p95=59.88m): 269

## Simulated detection latency
- Automated (15-min polling): median 8 min, p95 15 min
- Manual (daily 09:00 review): median 689 min, p95 1373 min

Note: the automated design polls every 15 minutes; the observed simulated median detection
latency is 8 minutes (event -> next poll + processing), versus a simulated manual
median of 689 minutes. Figures are from this synthetic simulation, not a live tenant.
