import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def test_pipeline_transform_shape():
    frame = pd.DataFrame(
        {
            "age": [40, 50, 60, 70],
            "cholesterol": [200, 250, 180, 300],
            "sex": [1, 0, 1, 0],
            "target": [0, 1, 0, 1],
        }
    )
    X = frame.drop(columns=["target"])

    numeric = ["age", "cholesterol"]
    categorical = ["sex"]

    pre = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric,
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

    transformed = pre.fit_transform(X)
    assert transformed.shape[0] == len(X)
    assert transformed.shape[1] >= 3
