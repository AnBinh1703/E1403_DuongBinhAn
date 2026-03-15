# Data Governance & Monitoring

## Data Security

- PHI/PII handling under HIPAA-like controls.
- AES-256 encryption at rest; TLS in transit.
- RBAC with least privilege.

## KPI Monitoring

- AUC-ROC >= 0.90
- Recall >= 0.90
- FNR < 12%
- Latency P95 < 100ms

## Drift & Retraining

- KS drift > 0.10: investigate.
- KS drift > 0.15: trigger retraining.
- Scheduled retrain: every 6 months.
- Triggered retrain: AUC drop > 3%.

## Audit Logging

- Log prediction timestamp, model version, and key feature summary.
- Keep immutable run logs in `outputs/logs/`.
