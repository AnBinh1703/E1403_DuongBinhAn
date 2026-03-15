# Deployment Playbook

## Scope

Deploy heart disease risk scoring as batch/micro-batch service with explainability and monitoring.

## Environments

- Dev: local notebook + scripts.
- Staging: Docker Compose with Dask scheduler/workers.
- Production: containerized services + RBAC + audit logs.

## Deployment Steps

1. `docker compose build`
2. `docker compose up -d`
3. Verify Dask cluster and Jupyter health.
4. `python scripts/save_models.py`
5. `python scripts/benchmarks.py --sizes 10000 100000 500000`
6. `python scripts/fairness_analysis.py`
7. Publish model + threshold policy.

## Model Release Checklist

- Metrics stable and within tolerance.
- Threshold policy approved (default 0.05).
- SHAP global + local visuals generated.
- Drift/retrain policy active.
- Audit logging enabled.
