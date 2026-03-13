# 🔮 SHAP QUICK START GUIDE

## Running SHAP Local Explainability Analysis

### **Installation**

```bash
# Option 1: Install from requirements
pip install -r notebook/requirements.txt

# Option 2: Install SHAP specifically
pip install shap>=0.12.0
```

### **Running SHAP in Your Notebook**

#### **Step 1: Navigate to SHAP Section**
In your Jupyter notebook, find the cell titled:
> **"9.2 Local Explainability: SHAP (SHapley Additive exPlanations)"**

#### **Step 2: Run SHAP Cells Sequentially**

Cell 1: **SHAP Conceptual Framework** (Markdown)
- Read this to understand why local explanations matter
- Real patient case example included

Cell 2: **SHAP Implementation** (Code - 170 lines)
- Installs SHAP automatically
- Creates TreeExplainer for Random Forest
- Generates 3 types of visualizations

Cell 3: **Clinical Application Guide** (Markdown)
- Explains how to interpret SHAP outputs
- Shows concrete clinical examples

#### **Step 3: Interpret the 3 Visualizations**

**Output 1: SHAP Summary Bar Plot**
```
The X-axis shows the average absolute SHAP value for each feature
Higher bar = more important for predictions
Colors indicate direction (red=increases risk, blue=decreases risk)
```

**Output 2: SHAP Dependence Plots (4 plots)**
```
X-axis: Feature value (e.g., age in years)
Y-axis: SHAP value (contribution to prediction)
Shows how each feature drives risk across the range of values
Colored by another feature that may have interaction
```

**Output 3: Individual Patient Explanations (3 cases)**
```
HIGH-RISK PATIENT: ~80% probability of disease
├─ Exercise angina: +0.25 (major driver)
├─ ST slope: +0.20 (moderate driver)
├─ Age: +0.18 (moderate driver)
└─ Max heart rate: -0.10 (protective)

MEDIUM-RISK PATIENT: ~50% probability
└─ Balanced positive and negative factors

LOW-RISK PATIENT: ~20% probability
└─ Protected by favorable factors
```

---

## **Clinical Interpretation Guide**

### **For Each Patient, You Get:**

| Information | What It Means | Action |
|-------------|-------|--------|
| Probability | Patient X has 72% risk of heart disease | Clinical assessment needed |
| Top Risk Drivers | Exercise angina, ST elevation, age | Target interventions on these |
| Protective Factors | High max heart rate achieved, normal BP | Build on these strengths |
| Modifiable vs Fixed | Cholesterol (modifiable), age (fixed) | Prioritize lifestyle changes |

### **Example Clinical Translation**

```
MODEL OUTPUT:
Model prediction: 72% risk
Top drivers:
  - ST elevation during exercise → +25%
  - Age 58 → +18%
  - Cholesterol 270 → +15%

CLINICAL ACTION:
1. URGENT: Order ECG stress test (ST elevation sign)
2. MODERATE: Start statin therapy + BP management
3. ONGOING: Lifestyle modification counseling
4. FOLLOW-UP: Repeat screening in 3 months
```

---

## **Troubleshooting**

### **Common Issues**

| Problem | Solution |
|---------|----------|
| ImportError: No module named 'shap' | Run: `pip install shap>=0.12.0` |
| Memory error on large dataset | Reduce sample size from 100 to 50: `X_shap = X_test.iloc[:50]` |
| SHAP plot not showing | Ensure Jupyter has matplotlib backend: Add `%matplotlib inline` at top |
| Slow computation | TreeExplainer is fast, but ensure your RAM has ~2GB free |

### **Performance Tips**

- **Quick SHAP** (< 1 min): 50 patient samples
- **Standard SHAP** (2-3 min): 100 patient samples  
- **Comprehensive SHAP** (5-10 min): 200+ patient samples

---

## **Next Steps After Running SHAP**

### **1. Export Visualizations** (For Your Report)

```python
# In a new cell, add:
import os
output_dir = 'outputs/figures'
os.makedirs(output_dir, exist_ok=True)

# SHAP plots save as PNG
# Move them to outputs/figures/ for LaTeX report
```

### **2. Integrate into LaTeX Report**

```latex
\section{Local Explainability: SHAP Analysis}
\subsection{Global Feature Importance via SHAP}
\includegraphics[width=0.8\textwidth]{figures/shap_summary.png}

\subsection{Patient Case Study}
As shown in Figure X, for a 58-year-old patient...
```

### **3. Create Presentation Slides**

Use SHAP plots to explain:
- Feature importance ranking
- Patient-specific risk drivers
- Intervention prioritization

---

## **Key Metrics**

After running SHAP, you'll have:

- ✅ **11 SHAP values** per patient (for each feature)
- ✅ **1 Base value** (average model output across all patients)
- ✅ **3 Visualizations** (summary, dependence, force plots)
- ✅ **3 Patient case studies** (high, medium, low risk)
- ✅ **Interpretability documentation** for compliance

---

## **Publications & References**

The SHAP method you're using follows:

**Lundberg, S.M., & Lee, S.I. (2017)**
> "A Unified Approach to Interpreting Model Predictions"
> International Conference on Machine Learning (ICML)
> arXiv: https://arxiv.org/abs/1705.07874

**Key Concept**: SHAP uses game theory (Shapley values) to calculate each feature's contribution to changing the model output from a baseline value to the model's prediction for instance x.

---

## **Questions?**

Refer back to these sections in your notebook:
1. Section 9.2: SHAP Conceptual Framework
2. Section 9.3: Clinical Application Guide
3. Section 11, Recommendation #6: SHAP Dashboard Implementation

**Good luck with your analysis! 🎓**
