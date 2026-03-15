from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42


def build_preprocessor(frame: pd.DataFrame):
    categorical = [name for name in frame.columns if frame[name].dtype == "object"]
    numerical = [name for name in frame.columns if name not in categorical]
    return ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numerical,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("ohe", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )


def main():
    root = Path(__file__).resolve().parents[1]
    data_file = root / "data" / "heart_statlog_cleveland_hungary_final.csv"
    models_dir = root / "outputs" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(data_file)
    target = "target" if "target" in frame.columns else "heart_disease"
    labels = frame[target]
    features = frame.drop(columns=[target])

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    pre = build_preprocessor(features)
    models = {
        "logistic": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE),
    }

    for name, model in models.items():
        pipe = Pipeline(steps=[("pre", pre), ("model", model)])
        pipe.fit(X_train, y_train)
        joblib.dump(pipe, models_dir / f"{name}.joblib")

    summary = {
        "random_state": RANDOM_STATE,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "models": sorted([path.name for path in models_dir.glob("*.joblib")]),
    }
    pd.DataFrame([summary]).to_csv(root / "outputs" / "models" / "model_export_summary.csv", index=False)

    print(f"Saved models to: {models_dir}")


if __name__ == "__main__":
    main()
