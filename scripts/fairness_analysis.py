from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score


def group_scores(df: pd.DataFrame, group: str, target: str, prediction: str):
    output = []
    for value, part in df.groupby(group):
        y_true = part[target]
        y_pred = part[prediction]
        output.append(
            {
                "group_feature": group,
                "group_value": value,
                "n": len(part),
                "accuracy": round(accuracy_score(y_true, y_pred), 4),
                "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
                "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
            }
        )
    return output


def main():
    root = Path(__file__).resolve().parents[1]
    data_file = root / "data" / "heart_statlog_cleveland_hungary_final.csv"
    table_dir = root / "outputs" / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(data_file)
    target = "target" if "target" in frame.columns else "heart_disease"

    score = frame["oldpeak"].fillna(frame["oldpeak"].median()) + frame["exercise angina"].fillna(0) * 0.8
    norm = (score - score.min()) / (score.max() - score.min() + 1e-9)
    frame["pred_proxy"] = (norm >= 0.5).astype(int)

    rows = []
    for group in ["sex", "chest pain type", "ST slope"]:
        if group in frame.columns:
            rows.extend(group_scores(frame, group, target, "pred_proxy"))

    result = pd.DataFrame(rows)
    result.to_csv(table_dir / "fairness_subgroup_metrics.csv", index=False)
    result.to_json(table_dir / "fairness_subgroup_metrics.json", orient="records", indent=2)

    print("Saved fairness tables.")


if __name__ == "__main__":
    main()
