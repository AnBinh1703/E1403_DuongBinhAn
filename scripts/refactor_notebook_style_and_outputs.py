import json
import re
from pathlib import Path

nb_path = Path(r"d:/UMEF/E1403_Big Data Analyst/E1403_DuongBinhAn/notebook/Heart_Disease_BigData_Analytics_Project.ipynb")
nb = json.loads(nb_path.read_text(encoding="utf-8"))

removed_banner_lines = 0
removed_latex_lines = 0
updated_mentions = 0

banner_re = re.compile(r"^\s*#\s*=+\s*$")
latex_dir_line_re = re.compile(r"LATEX_FIG_DIR|LATEX_TAB_DIR")

for cell in nb.get("cells", []):
    src = cell.get("source", [])
    if not isinstance(src, list):
        continue

    new_src = []
    for line in src:
        # Remove banner lines like '# ========' to keep concise style
        if banner_re.match(line):
            removed_banner_lines += 1
            continue

        # Remove explicit latex directory variable definitions/usages
        if "LATEX_FIG_DIR =" in line or "LATEX_TAB_DIR =" in line:
            removed_latex_lines += 1
            continue

        if "LATEX_FIG_DIR" in line or "LATEX_TAB_DIR" in line:
            # remove lines that only reference latex dirs (e.g., mkdir list, print paths)
            if "OUTPUTS_DIR" not in line and "TABLES_DIR" not in line and "FIGURES_DIR" not in line:
                removed_latex_lines += 1
                continue

        # Remove text suggesting export to latex folder in outputs print lines/comments
        if "LaTeX" in line and "outputs" not in line.lower() and "to_latex(" not in line:
            line = line.replace("LaTeX", "report tables")
            updated_mentions += 1

        # Ensure no path points to latex/ for write operations
        line = line.replace("/ \"latex\" / \"figures\"", "/ \"outputs\" / \"figures\"")
        line = line.replace("/ \"latex\" / \"tables\"", "/ \"outputs\" / \"tables\"")

        new_src.append(line)

    # clean excessive blank lines introduced by removals
    compact_src = []
    blank_streak = 0
    for line in new_src:
        if line.strip() == "":
            blank_streak += 1
        else:
            blank_streak = 0
        if blank_streak > 1:
            continue
        compact_src.append(line)

    cell["source"] = compact_src

# Update markdown wording in all cells
for cell in nb.get("cells", []):
    if cell.get("cell_type") != "markdown":
        continue
    src = cell.get("source", [])
    if not isinstance(src, list):
        continue
    new_src = []
    for line in src:
        if "đính kèm báo cáo LaTeX" in line:
            line = line.replace("đính kèm báo cáo LaTeX", "đính kèm báo cáo")
            updated_mentions += 1
        new_src.append(line)
    cell["source"] = new_src

nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Updated notebook: {nb_path}")
print(f"Removed banner lines: {removed_banner_lines}")
print(f"Removed latex dir lines: {removed_latex_lines}")
print(f"Updated text mentions: {updated_mentions}")
