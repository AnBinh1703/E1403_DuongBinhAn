import json
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap


def main():
    root = Path(__file__).resolve().parents[1]
    data_file = root / "data" / "heart_statlog_cleveland_hungary_final.csv"
    model_file = root / "outputs" / "models" / "random_forest.joblib"
    figures = root / "outputs" / "figures"
    logs = root / "outputs" / "logs"
    tables = root / "outputs" / "tables"
    for folder in [figures, logs, tables]:
        folder.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(data_file)
    target = "target" if "target" in frame.columns else "heart_disease"
    X = frame.drop(columns=[target]).head(200)

    pipe = joblib.load(model_file)
    pre = pipe.named_steps["pre"]
    model = pipe.named_steps["model"]
    X_pre = pre.transform(X)

    started = time.time()
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(X_pre, check_additivity=False)
    runtime = time.time() - started

    if isinstance(values, list):
        values = values[1] if len(values) > 1 else values[0]

    if hasattr(values, "shape") and len(values.shape) == 3:
        values = values[:, :, 1]

    feature_names = [f"f_{index}" for index in range(X_pre.shape[1])]

    summary_path = figures / "shap_summary.png"
    shap.summary_plot(values, X_pre, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(summary_path, dpi=200)
    plt.close()

    base_value = explainer.expected_value
    if hasattr(base_value, "__len__"):
        base_value = base_value[1] if len(base_value) > 1 else base_value[0]

    sample_indexes = [0, 1, 2]
    for idx in sample_indexes:
        row_values = values[idx]
        if hasattr(row_values, "shape") and len(row_values.shape) == 2:
            row_values = row_values[:, 1]

        exp = shap.Explanation(
            values=row_values,
            base_values=base_value,
            data=X_pre[idx],
            feature_names=feature_names,
        )
        shap.plots.waterfall(exp, max_display=10, show=False)
        plt.tight_layout()
        plt.savefig(figures / f"shap_waterfall_{idx}.png", dpi=200)
        plt.close()

    meta = {
        "rows_explained": int(X.shape[0]),
        "runtime_seconds": round(runtime, 4),
        "summary_plot": str(summary_path.name),
        "local_plots": [f"shap_waterfall_{idx}.png" for idx in sample_indexes],
    }
    with open(logs / "shap_runtime.json", "w", encoding="utf-8") as file:
        json.dump(meta, file, indent=2)
    pd.DataFrame([meta]).to_csv(tables / "shap_runtime.csv", index=False)

    print("Saved SHAP outputs and runtime metadata.")


if __name__ == "__main__":
    main()
