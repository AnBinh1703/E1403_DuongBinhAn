import json
from pathlib import Path

NOTEBOOK = Path(r"d:/UMEF/E1403_Big Data Analyst/E1403_DuongBinhAn/notebook/Heart_Disease_BigData_Analytics_Project.ipynb")

nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))

cleared = 0
for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        if cell.get("outputs"):
            cleared += 1
        cell["outputs"] = []
        cell["execution_count"] = None

NOTEBOOK.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Cleared outputs in {cleared} code cells.")
