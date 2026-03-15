# Heart Disease Big Data Analytics (A+ Upgrade)

This repository includes a full academic workflow plus A+ artifacts: reproducible scripts, model exports, benchmark logs, fairness analysis, and interactive SHAP dashboard.

## Quickstart

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run reproducibility bundle:

```powershell
./scripts/run_all.ps1
```

## Main Commands

- `python scripts/benchmarks.py --sizes 10000 100000 500000`
- `python scripts/save_models.py`
- `python scripts/fairness_analysis.py`
- `streamlit run apps/shap_dashboard.py`

## Core Outputs

- `outputs/logs/benchmarks.log`
- `outputs/benchmark_results.csv`
- `outputs/figures/benchmark_pandas_vs_dask.png`
- `outputs/figures/benchmark_resources.png`
- `outputs/models/*.joblib`
- `outputs/tables/fairness_subgroup_metrics.csv`
- `outputs/figures/shap_summary.png`

## Docker (Optional)

```powershell
docker compose up --build
```

Services:

- Jupyter
- Dask scheduler
- Dask workers
