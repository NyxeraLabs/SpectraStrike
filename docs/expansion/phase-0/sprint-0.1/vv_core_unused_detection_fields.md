# Sprint 36: Unused Detection-Related Fields (Static Audit)

- Generated at: `2026-03-03T14:33:31.399871+00:00`
- Method: column token occurrence count across VectorVue Python code with schema declaration blocks stripped from `vv_core.py`.
- Interpretation: very low/no usage may indicate legacy or unpopulated field paths.

| Table | Column | Token Occurrences |
|---|---|---:|
| `anomaly_detections` | `detection_timestamp` | 1 |
| `campaign_metrics` | `evasion_success_pct` | 1 |
| `engagement_reports` | `detection_evasion_success_rate` | 1 |
| `real_time_alerts` | `alert_timestamp` | 1 |
