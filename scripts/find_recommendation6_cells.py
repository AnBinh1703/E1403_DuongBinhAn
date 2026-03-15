import json
from pathlib import Path

p = Path("d:/UMEF/E1403_Big Data Analyst/E1403_DuongBinhAn/notebook/Heart_Disease_BigData_Analytics_Project.ipynb")
nb = json.loads(p.read_text(encoding="utf-8"))

for i, cell in enumerate(nb.get("cells", []), 1):
    src = "".join(cell.get("source", []))
    if "recommendation_6" in src or "Add Recommendation 6" in src or "RECOMMENDATION 6" in src:
        print(i, cell.get("id"), cell.get("cell_type"))
        print(src[:600].replace("\n", " "))
        print("---")
