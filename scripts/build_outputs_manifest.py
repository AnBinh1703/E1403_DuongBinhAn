import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    outputs = root / "outputs"
    manifest = {
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "files": [],
    }

    for item in sorted(outputs.rglob("*")):
        if item.is_file():
            manifest["files"].append(
                {
                    "path": str(item.relative_to(root)).replace("\\", "/"),
                    "size_bytes": item.stat().st_size,
                }
            )

    with open(outputs / "outputs_manifest.json", "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)

    print("Saved outputs_manifest.json")


if __name__ == "__main__":
    main()
