import json
from pathlib import Path

p = Path("d:/UMEF/E1403_Big Data Analyst/E1403_DuongBinhAn/notebook/Heart_Disease_BigData_Analytics_Project.ipynb")
nb = json.loads(p.read_text(encoding="utf-8"))

patterns = ["recommendation_6", "STRATEGIC RECOMMENDATIONS FOR LEADERSHIP", "recommendations = \"\"\"", "┏", "╔"]
for i, cell in enumerate(nb.get("cells", []), 1):
    src = "".join(cell.get("source", []))
    if any(pat in src for pat in patterns):
        print(i, cell.get("id"), cell.get("cell_type"), len(src))
        print(src[:220].replace("\n", " "))
        print("---")
