$ErrorActionPreference = "Stop"

python scripts/benchmarks.py --sizes 10000 100000 500000
python scripts/save_models.py
python scripts/fairness_analysis.py
python scripts/generate_shap_outputs.py
python scripts/build_outputs_manifest.py

Write-Host "All reproducibility scripts completed."
