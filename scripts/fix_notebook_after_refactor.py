import json
from pathlib import Path

nb_path = Path(r"d:/UMEF/E1403_Big Data Analyst/E1403_DuongBinhAn/notebook/Heart_Disease_BigData_Analytics_Project.ipynb")
nb = json.loads(nb_path.read_text(encoding="utf-8"))

fixed = 0
for cell in nb.get("cells", []):
    if cell.get("cell_type") != "code":
        continue
    src = cell.get("source", [])
    if not isinstance(src, list):
        continue

    for i, line in enumerate(src):
        if line.strip() == "for _d in [DATA_DIR, SHARDS_DIR, FIGURES_DIR, TABLES_DIR,":
            src[i] = "for _d in [DATA_DIR, SHARDS_DIR, FIGURES_DIR, TABLES_DIR]:"
            fixed += 1

    cell["source"] = src

nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("fixed_entries", fixed)
