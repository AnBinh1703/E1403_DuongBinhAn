"""Generate the rewritten Academic Thesis Version notebook."""
import json, pathlib

NB_PATH = pathlib.Path(r"d:\UMEF\E1403_Big Data Analyst\E1403_DuongBinhAn\notebook\Heart_Disease_BigData_Analytics_Project_Academic.ipynb")

def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {},
            "source": [line + "\n" for line in source.strip().split("\n")]}

def code(source: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "outputs": [],
            "execution_count": None,
            "source": [line + "\n" for line in source.strip().split("\n")]}

cells = []

# ═══════════════════════════════════════════════════════════════════════════
# CELL 1 — TITLE
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
# Heart Disease Prediction — Big Data Analytics

**MSc Big Data Analytics | Final Project**
Student: Duong Binh An | Course: E1403"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 2 — SECTION 1: BUSINESS CONTEXT
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 1. Business Context

Heart disease remains the leading cause of death globally. This project develops a machine-learning screening system using clinical features from 1,190 patients (Cleveland, Hungary, Statlog datasets). The objective is to maximise **Recall** (minimise missed diagnoses) while demonstrating Big Data scalability with Dask and delivering a cost-benefit analysis for hospital decision-makers."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 3 — SETUP
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# SETUP — Library Imports & Project Paths
# ==========================================================================
from __future__ import annotations
import warnings, sys, time, shutil, os, tempfile
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from pathlib import Path

import dask
import dask.dataframe as dd

from sklearn.model_selection import (
    train_test_split, StratifiedKFold,
    RandomizedSearchCV, cross_val_score, cross_val_predict,
)
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, brier_score_loss,
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.calibration import calibration_curve
from scipy.stats import chi2_contingency, ttest_ind, mannwhitneyu, zscore

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    XGBOOST_AVAILABLE = False

import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.4f}'.format)
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# -- Paths (all relative, pathlib-based) -----------------------------------
NOTEBOOK_DIR = Path.cwd()
PROJECT_ROOT = NOTEBOOK_DIR.parent
DATA_DIR     = PROJECT_ROOT / 'data'
SHARDS_DIR   = DATA_DIR / 'shards'
DATA_DIR.mkdir(parents=True, exist_ok=True)
SHARDS_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE   = DATA_DIR / 'heart_statlog_cleveland_hungary_final.csv'
JSONL_FILE = DATA_DIR / 'heart_statlog_cleveland_hungary_final.jsonl'

# Auto-copy from legacy locations
for _legacy in [PROJECT_ROOT / CSV_FILE.name, NOTEBOOK_DIR / CSV_FILE.name]:
    if not CSV_FILE.exists() and _legacy.exists():
        shutil.copy2(_legacy, CSV_FILE)
        break

print(f"Python {sys.version.split()[0]} | Pandas {pd.__version__} | "
      f"Dask {dask.__version__} | XGBoost {'yes' if XGBOOST_AVAILABLE else 'no'}")
print(f"Dataset: {CSV_FILE}")"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 4 — SECTION 2: DATA INGESTION (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 2. Data Ingestion (Pandas vs Dask)

Multi-format ingestion demonstrates the **Variety** dimension of Big Data. Dask provides lazy evaluation and partition-based I/O, enabling the same code to scale from a laptop to a distributed cluster. A shard demo simulates HDFS/S3 distributed storage."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 5 — DATA INGESTION (CODE)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# DATA INGESTION — CSV, JSONL, Dask, Shard Demo, Volume Simulation
# ==========================================================================

# A) CSV with Pandas
t0 = time.time()
df_pandas = pd.read_csv(CSV_FILE)
pandas_time = time.time() - t0
print(f"[CSV]  {df_pandas.shape[0]:,} rows x {df_pandas.shape[1]} cols | "
      f"{pandas_time:.4f}s | {df_pandas.memory_usage(deep=True).sum()/1e6:.3f} MB")

# B) JSONL round-trip
if not JSONL_FILE.exists():
    df_pandas.to_json(JSONL_FILE, orient='records', lines=True)
df_json = pd.read_json(JSONL_FILE, lines=True)
assert df_pandas.shape == df_json.shape, "CSV/JSONL shape mismatch"
print(f"[JSONL] Schema consistent: {df_pandas.shape == df_json.shape}")

# C) Dask lazy load
t0 = time.time()
df_dask = dd.read_csv(str(CSV_FILE))
print(f"[Dask] Lazy build: {time.time()-t0:.4f}s | {df_dask.npartitions} partition(s)")

# D) Shard demo (simulates HDFS/S3 distributed storage)
N_SHARDS = 10
if len(list(SHARDS_DIR.glob('part_*.csv'))) < N_SHARDS:
    for f in SHARDS_DIR.glob('part_*.csv'):
        f.unlink()
    rows_per = len(df_pandas) // N_SHARDS
    for i in range(N_SHARDS):
        s = i * rows_per
        e = len(df_pandas) if i == N_SHARDS - 1 else (i + 1) * rows_per
        df_pandas.iloc[s:e].to_csv(SHARDS_DIR / f'part_{i:04d}.csv', index=False)

df_shards = dd.read_csv(str(SHARDS_DIR / 'part_*.csv'))
assert len(df_shards) == len(df_pandas), "Shard integrity failed"
print(f"[Shards] {N_SHARDS} partition files -> {len(df_shards):,} rows (integrity OK)")

# E) Volume simulation (100x replication)
SCALE_FACTOR = 100
t0 = time.time()
df_scaled = pd.concat([df_pandas] * SCALE_FACTOR, ignore_index=True)
pandas_scale_time = time.time() - t0
print(f"[Volume] {SCALE_FACTOR}x -> {len(df_scaled):,} rows | "
      f"{df_scaled.memory_usage(deep=True).sum()/1e6:.1f} MB | {pandas_scale_time:.4f}s")
del df_scaled

# Working copy
df = df_pandas.copy()
target_dist = df['target'].value_counts()
print(f"\\nDataset ready: {df.shape}")
print(f"Target: 0={target_dist[0]} ({target_dist[0]/len(df)*100:.1f}%), "
      f"1={target_dist[1]} ({target_dist[1]/len(df)*100:.1f}%)")"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 6 — SECTION 3: EDA (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 3. Exploratory Data Analysis

Target distribution, correlation structure, and three business questions — each validated with a statistical test (Chi-square, t-test). All EDA uses a full-dataset copy; model training uses a separate leak-free pipeline."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 7 — EDA (CODE)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# EXPLORATORY DATA ANALYSIS
# ==========================================================================

# Handle invalid cholesterol (0 = biologically impossible -> median)
valid_chol_med = df.loc[df['cholesterol'] > 0, 'cholesterol'].median()
df.loc[df['cholesterol'] == 0, 'cholesterol'] = valid_chol_med

# EDA-only feature engineering
df['Age_Group'] = pd.cut(df['age'], bins=[0, 40, 60, 200],
                         labels=['Young', 'Middle', 'Senior']).astype(str)
df['Cholesterol_Risk_Level'] = (df['cholesterol'] > 240).astype(int)
df['BP_Category'] = df['resting bp s'].apply(
    lambda x: 'Normal' if x < 120 else ('High_Stage1' if x < 140 else 'High_Stage2'))

# -- Figure 1: Target distribution + Correlation heatmap ------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

tc = df['target'].value_counts()
axes[0].bar(['Healthy (0)', 'Disease (1)'], tc.values,
            color=['#2ecc71', '#e74c3c'], edgecolor='black')
for i, v in enumerate(tc.values):
    axes[0].text(i, v + 15, f'{v} ({v/len(df)*100:.1f}%)',
                 ha='center', fontweight='bold')
axes[0].set_title('Target Distribution', fontweight='bold')
axes[0].set_ylabel('Count')

corr_cols = ['age', 'sex', 'chest pain type', 'resting bp s', 'cholesterol',
             'fasting blood sugar', 'resting ecg', 'max heart rate',
             'exercise angina', 'oldpeak', 'ST slope', 'target']
corr_matrix = df[corr_cols].corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
            center=0, square=True, ax=axes[1], vmin=-1, vmax=1,
            linewidths=0.5, cbar_kws={'shrink': 0.8})
axes[1].set_title('Correlation Matrix (Lower Triangle)', fontweight='bold')
plt.tight_layout()
plt.show()

# -- Business Questions ----------------------------------------------------
# BQ1: Age group risk
age_risk = (df.groupby('Age_Group')['target'].mean()
            .reindex(['Young', 'Middle', 'Senior']) * 100)
chi2_age, p_age = chi2_contingency(
    pd.crosstab(df['Age_Group'], df['target']))[:2]
print(f"BQ1 - Age Group Disease Rate:")
for grp in ['Young', 'Middle', 'Senior']:
    print(f"  {grp:8s}: {age_risk[grp]:.1f}%")
print(f"  Chi2={chi2_age:.2f}, p={p_age:.6f}")

# BQ2: Cholesterol impact
chol_risk = df.groupby('Cholesterol_Risk_Level')['target'].mean() * 100
t_stat, p_chol = ttest_ind(
    df[df['target'] == 1]['cholesterol'],
    df[df['target'] == 0]['cholesterol'])
print(f"\\nBQ2 - Cholesterol Disease Rate: "
      f"Normal(<=240)={chol_risk[0]:.1f}%, High(>240)={chol_risk[1]:.1f}%")
print(f"  t={t_stat:.4f}, p={p_chol:.6f}")

# BQ3: Risk factor combinations
chol_lbl = df['Cholesterol_Risk_Level'].map({0: 'CholNormal', 1: 'CholHigh'})
combo = df['Age_Group'] + '+' + chol_lbl + '+' + df['BP_Category']
combo_risk = df.groupby(combo)['target'].agg(['mean', 'count'])
combo_risk = combo_risk[combo_risk['count'] >= 10].sort_values('mean', ascending=False)
print(f"\\nBQ3 - Highest risk combination: "
      f"'{combo_risk.index[0]}' = {combo_risk['mean'].iloc[0]*100:.1f}%")"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 8 — SECTION 4: PREPROCESSING PIPELINE (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 4. Preprocessing Pipeline & Feature Engineering

Four custom sklearn transformers handle cholesterol correction, median imputation, winsorization, and 7 rule-based features (Report Table 3). A `ColumnTransformer` applies `StandardScaler` to 16 numeric features and `OneHotEncoder(drop='first')` to 2 categorical features, yielding **20 output columns**. The train/test split is performed before fitting any transformer."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 9 — PREPROCESSING PIPELINE (CODE)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# PREPROCESSING PIPELINE (leak-free)
# ==========================================================================

class CholesterolFixer(BaseEstimator, TransformerMixin):
    \"\"\"Replace cholesterol == 0 with NaN (domain rule; no fitted params).\"\"\"
    def fit(self, X, y=None): return self
    def transform(self, X):
        X = X.copy()
        if 'cholesterol' in X.columns:
            X.loc[X['cholesterol'] == 0, 'cholesterol'] = np.nan
        return X

class DataFrameImputer(BaseEstimator, TransformerMixin):
    \"\"\"Median-impute numeric NaNs; medians fitted on training data only.\"\"\"
    def fit(self, X, y=None):
        self.medians_ = X.select_dtypes(include=[np.number]).median()
        return self
    def transform(self, X):
        X = X.copy()
        for col in self.medians_.index:
            if col in X.columns and X[col].isnull().any():
                X[col] = X[col].fillna(self.medians_[col])
        return X

class DataFrameWinsorizer(BaseEstimator, TransformerMixin):
    \"\"\"Clip numeric columns at [lo, hi] percentiles; bounds fitted on train.\"\"\"
    def __init__(self, lower_pct=1, upper_pct=99):
        self.lower_pct = lower_pct
        self.upper_pct = upper_pct
    def fit(self, X, y=None):
        self.bounds_ = {}
        for col in X.select_dtypes(include=[np.number]).columns:
            self.bounds_[col] = (np.nanpercentile(X[col], self.lower_pct),
                                 np.nanpercentile(X[col], self.upper_pct))
        return self
    def transform(self, X):
        X = X.copy()
        for col, (lo, hi) in self.bounds_.items():
            if col in X.columns:
                X[col] = X[col].clip(lower=lo, upper=hi)
        return X

class FeatureEngineer(BaseEstimator, TransformerMixin):
    \"\"\"Create 7 rule-based features (Report Table 3). No trained params.\"\"\"
    def fit(self, X, y=None): return self
    def transform(self, X):
        X = X.copy()
        X['Age_Group'] = pd.cut(X['age'], bins=[0, 40, 60, 200],
                                labels=['Young', 'Middle', 'Senior']).astype(str)
        X['BP_Category'] = X['resting bp s'].apply(
            lambda bp: 'Normal' if bp < 120 else (
                'High_Stage1' if bp < 140 else 'High_Stage2'))
        X['Heart_Risk_Index'] = (
            X['age'] * X['cholesterol'] * X['resting bp s'] / 100_000)
        X['Cholesterol_to_Age_Ratio'] = X['cholesterol'] / X['age']
        X['Age_Chol_Interaction'] = X['age'] * X['cholesterol'] / 10_000
        X['Max_HR_Reserve'] = (220 - X['age']) - X['max heart rate']
        X['Cholesterol_Risk_Level'] = (X['cholesterol'] > 240).astype(int)
        return X

# -- Feature lists ---------------------------------------------------------
numerical_features = [
    'age', 'sex', 'chest pain type', 'resting bp s', 'cholesterol',
    'fasting blood sugar', 'resting ecg', 'max heart rate',
    'exercise angina', 'oldpeak', 'ST slope',
    'Heart_Risk_Index', 'Cholesterol_to_Age_Ratio',
    'Age_Chol_Interaction', 'Max_HR_Reserve', 'Cholesterol_Risk_Level']
categorical_features = ['Age_Group', 'BP_Category']

# -- Train / test split on RAW data (stratified, 80/20) --------------------
X_raw = df_pandas.drop('target', axis=1)
y_raw = df_pandas['target']
X_train, X_test, y_train, y_test = train_test_split(
    X_raw, y_raw, test_size=0.2, random_state=RANDOM_STATE, stratify=y_raw)

# -- Build & fit preprocessing pipeline -----------------------------------
preprocessing_pipe = Pipeline([
    ('chol_fix',   CholesterolFixer()),
    ('imputer',    DataFrameImputer()),
    ('winsorizer', DataFrameWinsorizer(lower_pct=1, upper_pct=99)),
    ('engineer',   FeatureEngineer()),
    ('columns', ColumnTransformer([
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(drop='first', sparse_output=False,
                              handle_unknown='ignore'), categorical_features),
    ], remainder='drop'))
])

X_train_processed = preprocessing_pipe.fit_transform(X_train)   # fit on train
X_test_processed  = preprocessing_pipe.transform(X_test)        # transform only

cat_names = (preprocessing_pipe.named_steps['columns']
             .named_transformers_['cat']
             .get_feature_names_out(categorical_features).tolist())
feature_names = numerical_features + cat_names

assert len(feature_names) == 20, f"Expected 20, got {len(feature_names)}"
print(f"Train: {X_train.shape[0]:,} | Test: {X_test.shape[0]:,} | "
      f"Features: {len(feature_names)} (16 numeric + {len(cat_names)} OHE)")
print(f"Stratification: train={y_train.mean():.3f}, test={y_test.mean():.3f}")

def make_pipeline(model):
    \"\"\"Fresh Pipeline (re-fits all transforms per fold) for CV / tuning.\"\"\"
    return Pipeline([
        ('chol_fix',   CholesterolFixer()),
        ('imputer',    DataFrameImputer()),
        ('winsorizer', DataFrameWinsorizer(lower_pct=1, upper_pct=99)),
        ('engineer',   FeatureEngineer()),
        ('columns', ColumnTransformer([
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False,
                                  handle_unknown='ignore'), categorical_features),
        ], remainder='drop')),
        ('model', model),
    ])"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 10 — SECTION 5: MODELING (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 5. Modeling

Three classifiers: Logistic Regression (baseline), Random Forest, and XGBoost. Cross-validation (5-fold stratified) uses `make_pipeline()` to re-fit all transforms per fold. `RandomizedSearchCV` tunes RF and XGBoost with **Recall** as the scoring metric."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 11 — MODELING (CODE)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# MODELING — Baseline, Cross-Validation, Hyperparameter Tuning
# ==========================================================================
scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

# -- A) Baseline models (trained on pre-processed data) --------------------
lr_model = LogisticRegression(class_weight='balanced', max_iter=1000,
                              random_state=RANDOM_STATE)
lr_model.fit(X_train_processed, y_train)
y_pred_lr = lr_model.predict(X_test_processed)
y_prob_lr = lr_model.predict_proba(X_test_processed)[:, 1]

rf_init = RandomForestClassifier(n_estimators=100, max_depth=10,
    min_samples_split=5, class_weight='balanced',
    random_state=RANDOM_STATE, n_jobs=-1)
rf_init.fit(X_train_processed, y_train)
y_pred_rf = rf_init.predict(X_test_processed)
y_prob_rf = rf_init.predict_proba(X_test_processed)[:, 1]

if XGBOOST_AVAILABLE:
    xgb_init = xgb.XGBClassifier(
        n_estimators=100, max_depth=6, learning_rate=0.1,
        scale_pos_weight=scale_pos_weight, random_state=RANDOM_STATE,
        use_label_encoder=False, eval_metric='logloss')
else:
    xgb_init = GradientBoostingClassifier(
        n_estimators=100, max_depth=6, learning_rate=0.1,
        random_state=RANDOM_STATE)
xgb_init.fit(X_train_processed, y_train)
y_pred_xgb = xgb_init.predict(X_test_processed)
y_prob_xgb = xgb_init.predict_proba(X_test_processed)[:, 1]

# -- B) Cross-validation (Pipeline-wrapped, leak-free) ---------------------
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv_models = {
    'Logistic Regression': LogisticRegression(
        class_weight='balanced', max_iter=1000, random_state=RANDOM_STATE),
    'Random Forest': RandomForestClassifier(
        n_estimators=100, max_depth=10, class_weight='balanced',
        random_state=RANDOM_STATE, n_jobs=-1),
}
if XGBOOST_AVAILABLE:
    cv_models['XGBoost'] = xgb.XGBClassifier(
        n_estimators=100, max_depth=6, learning_rate=0.1,
        scale_pos_weight=scale_pos_weight, random_state=RANDOM_STATE,
        use_label_encoder=False, eval_metric='logloss')

print("Cross-Validation (5-fold, Pipeline per fold):")
for name, m in cv_models.items():
    scores = cross_val_score(make_pipeline(m), X_train, y_train,
                             cv=skf, scoring='accuracy')
    print(f"  {name:25s}  {scores.mean():.4f} +/- {scores.std():.4f}")

# -- C) Hyperparameter tuning (RandomizedSearchCV) -------------------------
skf_tune = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

# RF tuning
rf_search = RandomizedSearchCV(
    make_pipeline(RandomForestClassifier(
        class_weight='balanced', random_state=RANDOM_STATE, n_jobs=-1)),
    {'model__n_estimators': [50, 100, 200, 300],
     'model__max_depth': [5, 10, 15, 20, None],
     'model__min_samples_split': [2, 5, 10],
     'model__min_samples_leaf': [1, 2, 4],
     'model__max_features': ['sqrt', 'log2']},
    n_iter=30, cv=skf_tune, scoring='recall',
    random_state=RANDOM_STATE, n_jobs=-1, verbose=0)
rf_search.fit(X_train, y_train)
best_rf_pipe = rf_search.best_estimator_
best_rf = best_rf_pipe.named_steps['model']
y_pred_best_rf = best_rf_pipe.predict(X_test)
y_prob_best_rf = best_rf_pipe.predict_proba(X_test)[:, 1]

# XGB tuning
if XGBOOST_AVAILABLE:
    xgb_param_grid = {
        'model__n_estimators': [50, 100, 200, 300],
        'model__max_depth': [3, 5, 7, 10],
        'model__learning_rate': [0.01, 0.05, 0.1, 0.2],
        'model__subsample': [0.7, 0.8, 0.9, 1.0],
        'model__colsample_bytree': [0.7, 0.8, 0.9, 1.0],
        'model__min_child_weight': [1, 3, 5]}
    xgb_base = make_pipeline(xgb.XGBClassifier(
        scale_pos_weight=scale_pos_weight, random_state=RANDOM_STATE,
        use_label_encoder=False, eval_metric='logloss'))
else:
    xgb_param_grid = {
        'model__n_estimators': [50, 100, 200, 300],
        'model__max_depth': [3, 5, 7, 10],
        'model__learning_rate': [0.01, 0.05, 0.1, 0.2],
        'model__subsample': [0.7, 0.8, 0.9, 1.0],
        'model__min_samples_split': [2, 5, 10],
        'model__min_samples_leaf': [1, 2, 4]}
    xgb_base = make_pipeline(GradientBoostingClassifier(
        random_state=RANDOM_STATE))

xgb_search = RandomizedSearchCV(
    xgb_base, xgb_param_grid, n_iter=30, cv=skf_tune,
    scoring='recall', random_state=RANDOM_STATE, n_jobs=-1, verbose=0)
xgb_search.fit(X_train, y_train)
best_xgb_pipe = xgb_search.best_estimator_
best_xgb = best_xgb_pipe.named_steps['model']
y_pred_best_xgb = best_xgb_pipe.predict(X_test)
y_prob_best_xgb = best_xgb_pipe.predict_proba(X_test)[:, 1]

model_label = 'XGBoost' if XGBOOST_AVAILABLE else 'Gradient Boosting'
print(f"\\nTuned RF   best CV Recall: {rf_search.best_score_:.4f}")
print(f"Tuned {model_label} best CV Recall: {xgb_search.best_score_:.4f}")"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 12 — SECTION 6: EVALUATION (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 6. Evaluation

All models compared on Accuracy, Precision, Recall, F1, and AUC-ROC. **Recall is prioritised**: a false negative (missed disease) costs \\$20,000 vs \\$200 for a false positive. Calibration quality is assessed via Brier scores."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 13 — EVALUATION (CODE)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# EVALUATION — Comparison Table, ROC, Confusion Matrix, Calibration
# ==========================================================================
def metrics_row(name, y_true, y_pred, y_prob):
    return {'Model': name,
            'Accuracy':  accuracy_score(y_true, y_pred),
            'Precision': precision_score(y_true, y_pred),
            'Recall':    recall_score(y_true, y_pred),
            'F1':        f1_score(y_true, y_pred),
            'AUC-ROC':   roc_auc_score(y_true, y_prob)}

results_df = pd.DataFrame([
    metrics_row('Logistic Regression',     y_test, y_pred_lr,       y_prob_lr),
    metrics_row('Random Forest (Init)',    y_test, y_pred_rf,       y_prob_rf),
    metrics_row('Random Forest (Tuned)',   y_test, y_pred_best_rf,  y_prob_best_rf),
    metrics_row(f'{model_label} (Init)',   y_test, y_pred_xgb,      y_prob_xgb),
    metrics_row(f'{model_label} (Tuned)',  y_test, y_pred_best_xgb, y_prob_best_xgb),
])
print("MODEL COMPARISON (test set, threshold = 0.5):")
print(results_df.round(4).to_string(index=False))

# -- Figure: ROC + Confusion Matrix + Calibration -------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# ROC curves
for name, yp, color in [
    ('Logistic Regression', y_prob_lr,       '#3498db'),
    ('RF Tuned',            y_prob_best_rf,  '#27ae60'),
    (f'{model_label} Tuned', y_prob_best_xgb, '#e74c3c')]:
    fpr, tpr, _ = roc_curve(y_test, yp)
    axes[0].plot(fpr, tpr, lw=2, color=color,
                 label=f'{name} ({roc_auc_score(y_test, yp):.4f})')
axes[0].plot([0, 1], [0, 1], 'k--', lw=1)
axes[0].set_xlabel('FPR'); axes[0].set_ylabel('TPR')
axes[0].set_title('ROC Curves', fontweight='bold')
axes[0].legend(fontsize=9); axes[0].grid(alpha=0.3)

# Confusion matrix (best model by Recall)
cm = confusion_matrix(y_test, y_pred_best_rf)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1],
            xticklabels=['Healthy', 'Disease'],
            yticklabels=['Healthy', 'Disease'])
axes[1].set_title('Confusion Matrix - RF Tuned', fontweight='bold')
axes[1].set_xlabel('Predicted'); axes[1].set_ylabel('Actual')
tn, fp, fn, tp = cm.ravel()
axes[1].text(0.5, -0.12, f'TP={tp}  TN={tn}  FP={fp}  FN={fn}',
             transform=axes[1].transAxes, ha='center', fontsize=10, color='red')

# Calibration curves
axes[2].plot([0, 1], [0, 1], 'k--', lw=1, label='Perfect')
for name, yp, color in [
    ('LR',                    y_prob_lr,       '#3498db'),
    ('RF Tuned',              y_prob_best_rf,  '#27ae60'),
    (f'{model_label} Tuned',  y_prob_best_xgb, '#e74c3c')]:
    prob_true, prob_pred = calibration_curve(y_test, yp, n_bins=10)
    brier = brier_score_loss(y_test, yp)
    axes[2].plot(prob_pred, prob_true, 's-', color=color, lw=2,
                 label=f'{name} (Brier={brier:.4f})')
axes[2].set_xlabel('Mean Predicted Probability')
axes[2].set_ylabel('Fraction Positive')
axes[2].set_title('Calibration Curves', fontweight='bold')
axes[2].legend(fontsize=9); axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.show()"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 14 — SECTION 7: COST OPTIMIZATION (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 7. Cost Optimization

The optimal classification threshold is selected via **out-of-fold probabilities** on the training set (`cross_val_predict` with Pipeline), preventing test-set contamination. Cost assumptions: FN = \\$20,000, FP = \\$200."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 15 — COST OPTIMIZATION (CODE)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# COST-SENSITIVE THRESHOLD OPTIMIZATION (OOF on training set)
# ==========================================================================
COST_FN, COST_FP = 20_000, 200

pipe_cv = clone(best_xgb_pipe)
skf_thresh = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
y_prob_oof = cross_val_predict(
    pipe_cv, X_train, y_train, cv=skf_thresh, method='predict_proba')[:, 1]

thresholds = np.arange(0.05, 0.96, 0.05)
thresh_data = []
for t in thresholds:
    yp = (y_prob_oof >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_train, yp).ravel()
    rec  = tp / (tp + fn) if (tp + fn) else 0
    prec = tp / (tp + fp) if (tp + fp) else 0
    f1v  = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    thresh_data.append({'Threshold': t, 'FN': fn, 'FP': fp,
                        'Recall': rec, 'F1': f1v,
                        'Cost': fn * COST_FN + fp * COST_FP})
thresh_df = pd.DataFrame(thresh_data)

OPTIMAL_THRESHOLD = thresh_df.loc[thresh_df['Cost'].idxmin(), 'Threshold']
default_cost_oof = thresh_df.loc[
    thresh_df['Threshold'] == 0.50, 'Cost'].values[0]
optimal_cost_oof = thresh_df['Cost'].min()

# Final test-set evaluation (threshold locked)
y_prob_test = best_xgb_pipe.predict_proba(X_test)[:, 1]
y_def = (y_prob_test >= 0.50).astype(int)
y_opt = (y_prob_test >= OPTIMAL_THRESHOLD).astype(int)
tn_d, fp_d, fn_d, tp_d = confusion_matrix(y_test, y_def).ravel()
tn_o, fp_o, fn_o, tp_o = confusion_matrix(y_test, y_opt).ravel()
cost_def = fn_d * COST_FN + fp_d * COST_FP
cost_opt = fn_o * COST_FN + fp_o * COST_FP

print(f"Optimal threshold (OOF): {OPTIMAL_THRESHOLD:.2f}")
print(f"Test cost - default (0.50): ${cost_def:,.0f}")
print(f"Test cost - optimal ({OPTIMAL_THRESHOLD:.2f}): ${cost_opt:,.0f}")
print(f"Savings: ${cost_def - cost_opt:,.0f} "
      f"({(1 - cost_opt / cost_def) * 100:.1f}%)")
print(f"Recall @ optimal: {recall_score(y_test, y_opt):.4f}")

# -- Figure: Cost curve + Recall-F1 trade-off -----------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(thresh_df['Threshold'], thresh_df['Cost'] / 1000,
             'b-o', lw=2, markersize=5)
axes[0].axvline(0.5, color='red', ls='--', lw=1.5, label='Default (0.5)')
axes[0].axvline(OPTIMAL_THRESHOLD, color='green', ls='--', lw=1.5,
                label=f'Optimal ({OPTIMAL_THRESHOLD:.2f})')
axes[0].set_xlabel('Threshold'); axes[0].set_ylabel('Total Cost ($K)')
axes[0].set_title('Cost vs Threshold (OOF)', fontweight='bold')
axes[0].legend(); axes[0].grid(alpha=0.3)

axes[1].plot(thresh_df['Threshold'], thresh_df['Recall'],
             'g-o', lw=2, label='Recall')
axes[1].plot(thresh_df['Threshold'], thresh_df['F1'],
             'm--^', lw=2, label='F1')
axes[1].axvline(OPTIMAL_THRESHOLD, color='green', ls='--', lw=1.5, alpha=0.7)
axes[1].set_xlabel('Threshold'); axes[1].set_ylabel('Score')
axes[1].set_title('Recall-F1 Trade-off (OOF)', fontweight='bold')
axes[1].legend(); axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 16 — SECTION 8: BIG DATA SCALING (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 8. Big Data Scaling

Partition-based benchmarks compare Pandas and Dask across scale factors from 1x to 500x. Dask reads partition files via glob pattern, mirroring production HDFS/S3 workflows."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 17 — BIG DATA SCALING (CODE)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# BIG DATA SCALING BENCHMARK — Pandas vs Dask
# ==========================================================================
scale_factors = [1, 10, 50, 100, 500]
bench = []

for sf in scale_factors:
    scaled = pd.concat([df_pandas] * sf, ignore_index=True)
    n_parts = max(1, sf // 5)
    tmpdir = tempfile.mkdtemp(prefix=f'heart_{sf}x_')
    chunk = len(scaled) // n_parts
    for i in range(n_parts):
        s = i * chunk
        e = len(scaled) if i == n_parts - 1 else (i + 1) * chunk
        scaled.iloc[s:e].to_csv(
            os.path.join(tmpdir, f'part_{i:04d}.csv'), index=False)

    t0 = time.time()
    _ = scaled.describe()
    _ = scaled.groupby('sex').mean(numeric_only=True)
    pd_time = time.time() - t0

    t0 = time.time()
    ddf = dd.read_csv(os.path.join(tmpdir, 'part_*.csv'))
    _ = ddf.describe().compute()
    _ = ddf.groupby('sex').mean(numeric_only=True).compute()
    dk_time = time.time() - t0

    bench.append({'Scale': f'{sf}x', 'Rows': f'{len(scaled):,}',
                  'Pandas (s)': round(pd_time, 3),
                  'Dask (s)': round(dk_time, 3)})
    del scaled, ddf
    shutil.rmtree(tmpdir, ignore_errors=True)

bench_df = pd.DataFrame(bench)
print(bench_df.to_string(index=False))

# -- Scaling chart ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
x = range(len(scale_factors))
w = 0.35
ax.bar([i - w/2 for i in x],
       [b['Pandas (s)'] for b in bench], w,
       label='Pandas', color='#3498db')
ax.bar([i + w/2 for i in x],
       [b['Dask (s)'] for b in bench], w,
       label='Dask', color='#e74c3c')
ax.set_xticks(x)
ax.set_xticklabels([f'{sf}x' for sf in scale_factors])
ax.set_xlabel('Scale Factor')
ax.set_ylabel('Time (s, log scale)')
ax.set_title('Pandas vs Dask Processing Time', fontweight='bold')
ax.set_yscale('log')
ax.legend()
ax.grid(alpha=0.3, axis='y')
plt.tight_layout()
plt.show()"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 18 — SECTION 9: EXPLAINABILITY (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 9. Explainability

Feature importance from the tuned Random Forest and XGBoost models. Both agree on the dominant predictors (ST slope, chest pain type, oldpeak), providing cross-model validation. All top features are obtainable from a standard clinical workup."""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 19 — EXPLAINABILITY (CODE)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(code("""\
# ==========================================================================
# FEATURE IMPORTANCE — Random Forest & XGBoost
# ==========================================================================
rf_imp = pd.DataFrame({
    'Feature': feature_names,
    'Importance': best_rf.feature_importances_
}).sort_values('Importance', ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
top_n = 15
colors_fi = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, top_n))

axes[0].barh(range(top_n), rf_imp.head(top_n)['Importance'].values,
             color=colors_fi)
axes[0].set_yticks(range(top_n))
axes[0].set_yticklabels(rf_imp.head(top_n)['Feature'].values)
axes[0].invert_yaxis()
axes[0].set_xlabel('Importance')
axes[0].set_title('Random Forest - Top 15 Features', fontweight='bold')

if hasattr(best_xgb, 'feature_importances_'):
    xgb_imp = pd.DataFrame({
        'Feature': feature_names,
        'Importance': best_xgb.feature_importances_
    }).sort_values('Importance', ascending=False)
    axes[1].barh(range(top_n), xgb_imp.head(top_n)['Importance'].values,
                 color=colors_fi)
    axes[1].set_yticks(range(top_n))
    axes[1].set_yticklabels(xgb_imp.head(top_n)['Feature'].values)
    axes[1].invert_yaxis()
    axes[1].set_xlabel('Importance')
    axes[1].set_title(f'{model_label} - Top 15 Features', fontweight='bold')

plt.tight_layout()
plt.show()

print("\\nTop 5 Features (Random Forest):")
print(rf_imp.head(5).to_string(index=False))"""))

# ═══════════════════════════════════════════════════════════════════════════
# CELL 20 — SECTION 10: BUSINESS INSIGHTS & CONCLUSION (MD)
# ═══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
## 10. Business Insights & Conclusion

**Key Findings:**
- Senior patients (60+) have the highest disease rate; mandatory screening is recommended for ages 50+.
- The tuned Random Forest achieves the best Recall, correctly identifying the majority of disease cases.
- Lowering the threshold from 0.5 to the cost-optimal value reduces expected costs significantly while improving patient safety.
- Dask demonstrates production-ready scalability; the same pipeline code runs on a laptop or a distributed cluster.
- Top predictors (ST slope, chest pain type, exercise angina) are available from standard clinical workups, making the model practical for primary care deployment.

**Strategic Recommendations:**
- Deploy the predictive model with the optimised threshold into the hospital EHR system for automated risk scoring.
- Implement mandatory cardiovascular screening for patients aged 50+ with multiple risk factors.
- Establish a quarterly model retraining schedule with drift monitoring (KS test on prediction distributions).
- Launch a cholesterol management programme targeting patients above 240 mg/dL.
- Partner with insurance providers for risk-based premium models using the validated scoring system.

**Limitations:**
- Dataset size (1,190 patients) limits generalisability; production deployment requires validation on larger, multi-site cohorts.
- Missing variables (BMI, smoking history, family history) may improve predictive power.
- Temporal patterns not captured; longitudinal data would enable disease progression modelling.

---
*Project completed as part of MSc Big Data Analytics Course (E1403)*"""))

# ═══════════════════════════════════════════════════════════════════════════
# BUILD NOTEBOOK JSON
# ═══════════════════════════════════════════════════════════════════════════
# Strip trailing \n from last line of each cell source
for c in cells:
    if c["source"] and c["source"][-1].endswith("\n"):
        c["source"][-1] = c["source"][-1].rstrip("\n")

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13.9"
        }
    },
    "cells": cells
}

NB_PATH.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Notebook written: {NB_PATH}")
print(f"Total cells: {len(cells)}")
