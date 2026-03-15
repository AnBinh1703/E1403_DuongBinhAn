from pathlib import Path

import joblib
import pandas as pd
import shap
import streamlit as st

st.set_page_config(page_title="SHAP Dashboard", layout="wide")
st.title("Heart Disease SHAP Dashboard")

root = Path(__file__).resolve().parents[1]
data_file = root / "data" / "heart_statlog_cleveland_hungary_final.csv"
model_file = root / "outputs" / "models" / "random_forest.joblib"
fig_dir = root / "outputs" / "figures"
fig_dir.mkdir(parents=True, exist_ok=True)

if not data_file.exists() or not model_file.exists():
    st.error("Missing required artifacts. Run scripts/save_models.py first.")
    st.stop()

frame = pd.read_csv(data_file)
target = "target" if "target" in frame.columns else "heart_disease"
X = frame.drop(columns=[target])

pipe = joblib.load(model_file)
model = pipe.named_steps["model"]
pre = pipe.named_steps["pre"]

idx = st.number_input("Patient row", min_value=0, max_value=len(X) - 1, value=0)
row = X.iloc[[idx]]
probability = pipe.predict_proba(row)[0, 1]
st.metric("Predicted risk", f"{probability:.3f}")

X_small = X.head(200)
X_pre = pre.transform(X_small)
explainer = shap.TreeExplainer(model)
values = explainer.shap_values(X_pre, check_additivity=False)

if isinstance(values, list):
    values = values[1] if len(values) > 1 else values[0]

feature_names = [f"f_{i}" for i in range(X_pre.shape[1])]

st.subheader("Global SHAP")
summary_path = fig_dir / "shap_summary.png"
shap.summary_plot(values, X_pre, feature_names=feature_names, show=False)
import matplotlib.pyplot as plt
plt.tight_layout()
plt.savefig(summary_path, dpi=200)
plt.close()
st.image(str(summary_path))

st.subheader("Local SHAP")
local_index = int(min(idx, len(X_small) - 1))
waterfall_path = fig_dir / f"shap_waterfall_{local_index}.png"
exp = shap.Explanation(
    values=values[local_index],
    base_values=explainer.expected_value,
    data=X_pre[local_index],
    feature_names=feature_names,
)
shap.plots.waterfall(exp, max_display=10, show=False)
plt.tight_layout()
plt.savefig(waterfall_path, dpi=200)
plt.close()
st.image(str(waterfall_path))
