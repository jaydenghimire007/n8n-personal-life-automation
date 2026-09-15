import json
import pathlib
import sys

files = sorted(pathlib.Path("workflows").glob("*.json"))
print(f"Found {len(files)} file(s) in workflows/")

errors = []
for path in files:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        print(f"  OK: {path.name}")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name}: {exc}")

if errors:
    print("\nFAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("\nAll files valid JSON.")